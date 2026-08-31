"""
Graph Connection Queries.

Finds connection paths between entities (e.g. Bidder A to Bidder B through shared directors or addresses).
"""
import networkx as nx
import structlog
from typing import Dict, Any, List, Optional

logger = structlog.get_logger(__name__)

class GraphQueryEngine:
    def find_connection_path(
        self,
        G: nx.Graph,
        source_node_id: str,
        target_node_id: str,
    ) -> Dict[str, Any]:
        if not G.has_node(source_node_id) or not G.has_node(target_node_id):
            return {
                "connected": False,
                "path": [],
                "explanation": "One or both nodes do not exist in graph.",
            }

        try:
            path = nx.shortest_path(G, source=source_node_id, target=target_node_id)
            path_details = []
            for n in path:
                n_data = G.nodes[n]
                path_details.append({
                    "id": str(n),
                    "label": n_data.get("label"),
                    "type": n_data.get("type"),
                })

            return {
                "connected": True,
                "path_length": len(path) - 1,
                "path": path_details,
                "explanation": f"Connection path found across {len(path) - 1} hops.",
            }
        except nx.NetworkXNoPath:
            return {
                "connected": False,
                "path": [],
                "explanation": "No connection path exists between these entities.",
            }

graph_query_engine = GraphQueryEngine()
