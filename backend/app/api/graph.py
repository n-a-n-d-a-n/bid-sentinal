"""Graph API Router."""
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.engines.graph import GraphBuilderService, graph_analytics, graph_query_engine

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/graph")

@router.get("/bids/{bid_id}")
async def get_bid_graph(
    bid_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Returns network graph for a bid."""
    builder = GraphBuilderService(db)
    nx_graph = await builder.export_to_networkx()
    analytics = graph_analytics.analyze_graph(nx_graph)
    return {"bid_id": bid_id, **analytics}

@router.get("/bidders/{bidder_id}/connections/{target_bidder_id}")
async def get_bidders_connection(
    bidder_id: str,
    target_bidder_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Finds connection path between two bidders."""
    builder = GraphBuilderService(db)
    nx_graph = await builder.export_to_networkx()
    res = graph_query_engine.find_connection_path(nx_graph, bidder_id, target_bidder_id)
    return {"source_bidder_id": bidder_id, "target_bidder_id": target_bidder_id, **res}
