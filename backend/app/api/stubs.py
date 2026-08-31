"""Stub routers for graph, policies, decisions, demo, dataset, admin."""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ── Graph ──────────────────────────────────────────────────────────────────────
graph_router = APIRouter(prefix="/graph")

@graph_router.get("/bids/{bid_id}")
async def get_bid_graph(bid_id: str, current_user=Depends(get_current_user)):
    """Graph visualization data — Phase 6 implementation."""
    return {"nodes": [], "edges": [], "bid_id": bid_id, "status": "PHASE_6_PENDING"}

# ── Policies ───────────────────────────────────────────────────────────────────
policies_router = APIRouter(prefix="/policies")

@policies_router.get("")
async def list_policies(current_user=Depends(get_current_user)):
    """Policy knowledge base — Phase 8 implementation."""
    return {"items": [], "status": "PHASE_8_PENDING"}

@policies_router.post("/search")
async def search_policies(current_user=Depends(get_current_user)):
    """RAG policy search — Phase 8 implementation."""
    return {"answer": "Policy RAG not yet initialized.", "citations": [], "status": "PHASE_8_PENDING"}

# ── Decisions ──────────────────────────────────────────────────────────────────
decisions_router = APIRouter(prefix="/decisions")

@decisions_router.get("")
async def list_decisions(current_user=Depends(get_current_user)):
    """Officer decisions list — see /bids/{id}/decision for individual bid decisions."""
    return {"items": []}

# ── Demo ───────────────────────────────────────────────────────────────────────
demo_router = APIRouter(prefix="/demo")

@demo_router.get("/scenarios")
async def list_scenarios(current_user=Depends(get_current_user)):
    """Demo scenarios — Phase 10 implementation."""
    return {
        "scenarios": [
            {"id": "A", "name": "Clean Bidder", "description": "Fully compliant bidder", "status": "PENDING_IMPL"},
            {"id": "B", "name": "Turnover Failure", "description": "Turnover below threshold", "status": "PENDING_IMPL"},
            {"id": "C", "name": "Coordinated Network", "description": "Suspicious bidding network", "status": "PENDING_IMPL"},
            {"id": "D", "name": "GST Authority Conflict", "description": "Document says ACTIVE, authority says CANCELLED", "status": "PENDING_IMPL"},
            {"id": "E", "name": "API Unavailable", "description": "Government API unavailable scenario", "status": "PENDING_IMPL"},
            {"id": "F", "name": "OCR Ambiguity", "description": "Low OCR confidence", "status": "PENDING_IMPL"},
            {"id": "G", "name": "Corrigendum", "description": "Tender requirement changed by corrigendum", "status": "PENDING_IMPL"},
            {"id": "H", "name": "Officer Override", "description": "Officer overrides AI recommendation", "status": "PENDING_IMPL"},
        ]
    }

@demo_router.post("/scenarios/{scenario_id}/load")
async def load_scenario(scenario_id: str, current_user=Depends(get_current_user)):
    """Load a demo scenario — Phase 10 implementation."""
    return {"scenario_id": scenario_id, "status": "PHASE_10_PENDING", "message": "Demo scenario loading not yet implemented."}

# ── Dataset ────────────────────────────────────────────────────────────────────
dataset_router = APIRouter(prefix="/dataset")

@dataset_router.get("/status")
async def dataset_status(current_user=Depends(get_current_user)):
    return {"status": "PHASE_10_PENDING"}

# ── Admin ──────────────────────────────────────────────────────────────────────
admin_router = APIRouter(prefix="/admin")

@admin_router.get("/stats")
async def admin_stats(current_user=Depends(get_current_user)):
    """System statistics for admin dashboard."""
    return {"status": "ok", "version": "1.0.0"}
