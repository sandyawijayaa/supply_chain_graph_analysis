import networkx as nx
from typing import Dict, Any # <-- FIX: Import 'Any' and 'Dict' from typing

def analyze_graph(G: nx.MultiDiGraph) -> Dict[str, Any]:
    """
    Analyzes the graph to identify critical nodes and structural properties.
    This fulfills Step 2: analyze this graph.
    """
    analysis_results = {}

    # 1. Centrality Analysis (Identifying Bottlenecks/Hotspots)
    # Using Betweenness Centrality (a facility is important if it lies on many shortest paths)
    # and In-Degree Centrality (how many suppliers feed into it).

    # Betweenness Centrality: Identifies nodes that act as 'bridges'
    betweenness = nx.betweenness_centrality(G)
    top_bottlenecks = sorted(betweenness.items(), key=lambda item: item[1], reverse=True)[:3]
    analysis_results['Centrality_Bottlenecks'] = {
        'Description': "Nodes with high Betweenness Centrality are critical bottlenecks, as they connect otherwise separate parts of the supply chain.",
        'Top_Bottlenecks': top_bottlenecks
    }

    # In-Degree Centrality: Nodes with many incoming links (e.g., key aggregation points)
    in_degree = G.in_degree()
    # Convert degree view to a dictionary for sorting
    in_degree_dict = dict(in_degree)
    top_hubs = sorted(in_degree_dict.items(), key=lambda item: item[1], reverse=True)[:3]
    analysis_results['Centrality_Hubs'] = {
        'Description': "Nodes with high In-Degree Centrality are major consumption/assembly hubs.",
        'Top_Hubs': top_hubs
    }

    # 2. Clustering Analysis (Identifying Risk Regions/Communities)
    # We use a simple community detection algorithm (e.g., Louvain) for an undirected graph view
    # to find closely related groups.
    try:
        # Need to use the undirected version of the graph
        communities = list(nx.community.label_propagation_communities(G.to_undirected()))
        analysis_results['Clustering_Communities'] = {
            'Description': "Communities (clusters) represent densely connected groups, often indicating shared regional, organizational, or supply-path risks. If one node is affected, others in the community are highly susceptible.",
            'Communities': [list(c) for c in communities if len(c) > 1]
        }
    except Exception as e:
        analysis_results['Clustering_Communities'] = f"Clustering failed: {e}. Graph might be too sparse."


    # 3. Shortest Paths (Traceability & Emissions Reduction)
    start_node = "Foxconn Facility No. 3"
    end_node = "Brand A Distribution Center"
    try:
        shortest_path = nx.shortest_path(G, source=start_node, target=end_node)
        analysis_results['Shortest_Path'] = {
            'Description': f"The shortest path from '{start_node}' to '{end_node}' is crucial for calculating total lead time or emissions.",
            'Path': shortest_path,
            'Length': len(shortest_path) - 1
        }
    except nx.NetworkXNoPath:
        analysis_results['Shortest_Path'] = f"No path found between {start_node} and {end_node}."


    # 4. Connectivity/Failure Simulation (Simple Scenario)
    # What nodes contribute to Brand A DC?
    try:
        upstream_suppliers = list(nx.ancestors(G, "Brand A Distribution Center"))
        analysis_results['Upstream_Audit_Subgraph'] = {
            'Description': "Nodes contributing to the final product (Subgraph for audit/traceability).",
            'Suppliers_for_Brand_A': upstream_suppliers
        }
    except Exception as e:
        analysis_results['Upstream_Audit_Subgraph'] = f"Error during upstream calculation: {e}"


    return analysis_results