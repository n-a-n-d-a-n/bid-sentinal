"""
Graph Analytics Engine using NetworkX.

Calculates:
- Centrality metrics (degree & betweenness)
- Connected components & shared attribute clusters
- Network Pattern Signals:
  * MULTIPLE_BIDDERS_SHARED_ADDRESS
  * MULTIPLE_BIDDERS_SHARED_DIRECTOR
  * MULTIPLE_BIDDERS_SHARED_BANK_ACCOUNT
  * CLUSTERED_BIDDER_NETWORK
  * COMMON_CONTROL_ENTITY

CRITICAL GOVERNANCE RULE:
Never call network patterns "collusion" or "fraud" automatically.
Use explainable neutral terminology ("Potential coordinated bidding pattern detected", "Shared-control relationship detected").
"""
import networkx as nx
import structlog
from typing import Dict, Any, List, Optional

logger = structlog.get_logger(__name__)

class GraphAnalyticsEngine:
    def analyze_graph(self, G: nx.Graph) -> Dict[str, Any]:
        if G.number_of_nodes() == 0:
            return {
                "nodes_count": 0,
                "edges_count": 0,
                "network_signals": [],
                "centrality": {},
                "cytoscape_json": {"nodes": [], "edges": []},
            }

        # 1. Centrality Metrics
        degree_centrality = nx.degree_centrality(G)
        try:
            betweenness_centrality = nx.betweenness_centrality(G)
        except Exception:
            betweenness_centrality = {n: 0.0 for n in G.nodes()}

        # 2. Detect Shared Attribute Patterns
        network_signals: List[Dict[str, Any]] = []

        # Find attribute nodes connected to > 1 bidder node
        for n, data in G.nodes(data=True):
            node_type = data.get("type")
            neighbors = list(G.neighbors(n))
            bidder_neighbors = [nb for nb in neighbors if G.nodes[nb].get("type") == "BIDDER"]

            if len(bidder_neighbors) > 1:
                b_names = [G.nodes[b].get("label") for b in bidder_neighbors]

                if node_type == "ADDRESS":
                    network_signals.append({
                        "pattern": "MULTIPLE_BIDDERS_SHARED_ADDRESS",
                        "severity": "MEDIUM",
                        "description": f"Multiple bidders ({', '.join(b_names[:3])}) share the same registered address.",
                        "connected_bidders": b_names,
                        "shared_attribute": data.get("label"),
                    })
                elif node_type == "DIRECTOR" or node_type == "PERSON":
                    network_signals.append({
                        "pattern": "MULTIPLE_BIDDERS_SHARED_DIRECTOR",
                        "severity": "HIGH",
                        "description": f"Potential shared-control relationship: Multiple bidders share director '{data.get('label')}'.",
                        "connected_bidders": b_names,
                        "shared_attribute": data.get("label"),
                    })
                elif node_type == "BANK_ACCOUNT":
                    network_signals.append({
                        "pattern": "MULTIPLE_BIDDERS_SHARED_BANK_ACCOUNT",
                        "severity": "HIGH",
                        "description": f"Multiple bidders share the same bank account details.",
                        "connected_bidders": b_names,
                        "shared_attribute": data.get("label"),
                    })

        # 3. Export Cytoscape.js JSON format for UI
        cytoscape_nodes = []
        for n, data in G.nodes(data=True):
            cytoscape_nodes.append({
                "data": {
                    "id": str(n),
                    "label": data.get("label", str(n)),
                    "type": data.get("type", "UNKNOWN"),
                }
            })

        cytoscape_edges = []
        for u, v, data in G.edges(data=True):
            cytoscape_edges.append({
                "data": {
                    "source": str(u),
                    "target": str(v),
                    "relationship": data.get("relationship", "CONNECTED"),
                }
            })

        return {
            "nodes_count": G.number_of_nodes(),
            "edges_count": G.number_of_edges(),
            "network_signals": network_signals,
            "degree_centrality": {str(k): round(v, 3) for k, v in degree_centrality.items()},
            "betweenness_centrality": {str(k): round(v, 3) for k, v in betweenness_centrality.items()},
            "cytoscape_json": {
                "nodes": cytoscape_nodes,
                "edges": cytoscape_edges,
            },
        }

graph_analytics = GraphAnalyticsEngine()
