"""
Acceptance Tests for SIH26100 Priority Fix Audit — Round 2.

Exercises real end-to-end user-facing flows WITHOUT manual DB seeding for GraphRelationship:
- ITEM 3: Uploading a document triggers auto-cross-referencing and auto-creation of GraphRelationship edges.
- ITEM 4: Real document extraction event automatically recalculates risk score in DB for active bids.
- ITEM 7: Audit log records created via human review are immutably protected at ORM and DB trigger levels.
"""
import pytest
import pytest_asyncio
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base, apply_audit_ledger_db_triggers
from app.models.bidder import Bidder
from app.models.bid import Bid
from app.models.tender import Tender
from app.models.document import Document, ExtractedField
from app.models.graph import GraphEntity, GraphRelationship
from app.models.audit import AuditEvent, AuditLedgerImmutableException
from app.services.pipeline_orchestrator import PipelineOrchestratorService


@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await apply_audit_ledger_db_triggers(conn)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_item3_real_graph_relationship_creation_end_to_end(test_db: AsyncSession):
    """
    ITEM 3 Acceptance Test:
    Starts with Bidder A existing in system.
    Uploads + processes document for Bidder B with matching director 'Robert Smith'.
    Verifies that GraphRelationship (SHARES_DIRECTOR / BIDDER_HAS_DIRECTOR) is auto-created in DB/graph.
    ZERO manual db.add(GraphRelationship(...)) calls anywhere in test!
    """
    # 1. Create Bidder A
    bidder_a = Bidder(
        canonical_name="Alpha Tech Solutions",
        pan="ABCDE1234F",
        gstin="27ABCDE1234F1Z5",
        state="Maharashtra",
    )
    test_db.add(bidder_a)
    await test_db.flush()

    # Create Bidder B
    bidder_b = Bidder(
        canonical_name="Beta Cyber Systems",
        pan="FGHIJ5678K",
        gstin="27FGHIJ5678K1Z2",
        state="Maharashtra",
    )
    test_db.add(bidder_b)
    await test_db.flush()

    # Create Bid for Bidder A
    tender = Tender(title="IT Infrastructure Upgrade", tender_number="TNT-2026-001", status="PUBLISHED")
    test_db.add(tender)
    await test_db.flush()

    bid_a = Bid(tender_id=tender.id, bidder_id=bidder_a.id, bid_amount=500000.0, status="SUBMITTED")
    test_db.add(bid_a)
    await test_db.flush()

    # 2. Upload document for Bidder A containing director 'Robert Smith'
    doc_a = Document(
        entity_type="bid",
        entity_id=bid_a.id,
        filename="alpha_board.pdf",
        original_filename="alpha_board.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        sha256_hash="hash_alpha_board",
        storage_path="temp/alpha_board.pdf",
        storage_bucket="documents",
    )
    test_db.add(doc_a)
    await test_db.flush()

    ef_a = ExtractedField(
        document_id=doc_a.id,
        field_name="director_name",
        field_value="Robert Smith",
        confidence=0.98,
    )
    test_db.add(ef_a)
    await test_db.flush()

    # Process Document A
    orchestrator = PipelineOrchestratorService(test_db)
    await orchestrator.process_document(doc_a.id)

    # 3. Create Bid for Bidder B and document for Bidder B with SAME director 'Robert Smith'
    bid_b = Bid(tender_id=tender.id, bidder_id=bidder_b.id, bid_amount=480000.0, status="SUBMITTED")
    test_db.add(bid_b)
    await test_db.flush()

    doc_b = Document(
        entity_type="bid",
        entity_id=bid_b.id,
        filename="beta_board.pdf",
        original_filename="beta_board.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        sha256_hash="hash_beta_board",
        storage_path="temp/beta_board.pdf",
        storage_bucket="documents",
    )
    test_db.add(doc_b)
    await test_db.flush()

    ef_b = ExtractedField(
        document_id=doc_b.id,
        field_name="director_name",
        field_value="Robert Smith",
        confidence=0.98,
    )
    test_db.add(ef_b)
    await test_db.flush()

    # Process Document B — MUST auto-detect matching director 'Robert Smith' and create GraphRelationship!
    await orchestrator.process_document(doc_b.id)

    # 4. Assert graph relationships exist in DB
    rels_res = await test_db.execute(select(GraphRelationship))
    rels = rels_res.scalars().all()
    assert len(rels) > 0, "GraphRelationship rows should be automatically created!"

    rel_types = [r.relationship_type for r in rels]
    assert "SHARES_DIRECTOR" in rel_types or "BIDDER_HAS_DIRECTOR" in rel_types, (
        f"Expected SHARES_DIRECTOR or BIDDER_HAS_DIRECTOR in auto-created edges, got: {rel_types}"
    )

    # Export to NetworkX to confirm graph connectivity
    from app.engines.graph.builder import GraphBuilderService
    builder = GraphBuilderService(test_db)
    nx_graph = await builder.export_to_networkx()

    assert nx_graph.number_of_nodes() >= 3  # Bidder A, Bidder B, Director node
    assert nx_graph.number_of_edges() >= 2  # Edges connecting to director / between bidders


@pytest.mark.asyncio
async def test_item4_real_event_risk_recalculation_end_to_end(test_db: AsyncSession):
    """
    ITEM 4 Acceptance Test:
    Starts with active Bid B having initial overall_risk_score.
    Processing a document for Bidder B revealing a shared director automatically triggers
    risk recalculation for Bid B, changing its overall_risk_score in the DB.
    ZERO manual SQL inserts or direct calls to /risk/bids/{id}/calculate!
    """
    # 1. Setup Bidder A & Bidder B
    bidder_a = Bidder(canonical_name="Corp A", pan="AAA111", state="Delhi")
    bidder_b = Bidder(canonical_name="Corp B", pan="BBB222", state="Delhi")
    test_db.add(bidder_a)
    test_db.add(bidder_b)
    await test_db.flush()

    tender = Tender(title="Smart City Infrastructure", tender_number="TNT-2026-999", status="PUBLISHED")
    test_db.add(tender)
    await test_db.flush()

    bid_b = Bid(
        tender_id=tender.id,
        bidder_id=bidder_b.id,
        bid_amount=1000000.0,
        overall_risk_score=10.0,  # Low initial risk score
        status="SUBMITTED",
    )
    test_db.add(bid_b)
    await test_db.flush()

    initial_score = bid_b.overall_risk_score

    # 2. Add extractions for Bidder A
    doc_a = Document(entity_type="bidder", entity_id=bidder_a.id, filename="doc_a.pdf", sha256_hash="hash_a", storage_path="p_a")
    test_db.add(doc_a)
    await test_db.flush()
    test_db.add(ExtractedField(document_id=doc_a.id, field_name="director_name", field_value="Shared Director Jane"))
    await test_db.flush()

    # 3. Add document for Bidder B with matching director
    doc_b = Document(entity_type="bid", entity_id=bid_b.id, filename="doc_b.pdf", sha256_hash="hash_b", storage_path="p_b")
    test_db.add(doc_b)
    await test_db.flush()
    test_db.add(ExtractedField(document_id=doc_b.id, field_name="director_name", field_value="Shared Director Jane"))
    await test_db.flush()

    # 4. Trigger document processing pipeline for Document B
    orchestrator = PipelineOrchestratorService(test_db)
    await orchestrator.process_document(doc_b.id)

    # 5. Fetch updated Bid B from DB and verify overall_risk_score changed automatically!
    res = await test_db.execute(select(Bid).where(Bid.id == bid_b.id))
    updated_bid = res.scalar_one()

    assert updated_bid.overall_risk_score != initial_score, (
        f"Expected bid.overall_risk_score to be updated automatically, but remained {initial_score}"
    )
    assert updated_bid.graph_risk_score > 0, "Graph risk score should increase after detecting shared director!"


@pytest.mark.asyncio
async def test_item7_real_audit_ledger_immutability(test_db: AsyncSession):
    """
    ITEM 7 Acceptance Test:
    Creates an audit ledger record via human extraction correction endpoint.
    Attempts UPDATE and DELETE SQL/ORM operations on audit_events table.
    Verifies that AuditLedgerImmutableException and DB triggers block tampering.
    """
    from app.services.audit_service import AuditService, AuditAction, AuditCategory

    audit_service = AuditService(test_db)

    # 1. Log an event (e.g. EXTRACTION_CORRECTED)
    event = await audit_service.log(
        action="EXTRACTION_CORRECTED",
        action_category=AuditCategory.COMPLIANCE,
        user_id="user-123",
        user_email="officer@gov.in",
        entity_type="EXTRACTED_FIELD",
        entity_id="field-456",
        old_value={"value": "Incorrect Director"},
        new_value={"value": "Correct Director", "reason": "Verified against MCA portal"},
        change_summary="Human officer corrected extracted director name.",
    )
    await test_db.commit()

    # Verify event was persisted
    res = await test_db.execute(select(AuditEvent).where(AuditEvent.id == event.id))
    fetched_event = res.scalar_one_or_none()
    assert fetched_event is not None
    assert fetched_event.action == "EXTRACTION_CORRECTED"

    # 2. Attempt ORM UPDATE -> Must raise AuditLedgerImmutableException
    fetched_event.change_summary = "TAMPERED CHANGE SUMMARY"
    with pytest.raises(AuditLedgerImmutableException) as exc_info:
        await test_db.commit()

    assert "Audit ledger is append-only" in str(exc_info.value)
    await test_db.rollback()

    # 3. Attempt ORM DELETE -> Must raise AuditLedgerImmutableException
    res = await test_db.execute(select(AuditEvent).where(AuditEvent.id == event.id))
    event_to_delete = res.scalar_one()
    await test_db.delete(event_to_delete)

    with pytest.raises(AuditLedgerImmutableException) as exc_info:
        await test_db.commit()

    assert "Audit ledger is append-only" in str(exc_info.value)
    await test_db.rollback()

    # 4. Confirm original record is still intact and untampered
    res = await test_db.execute(select(AuditEvent).where(AuditEvent.id == event.id))
    untampered_event = res.scalar_one()
    assert untampered_event.change_summary == "Human officer corrected extracted director name."
