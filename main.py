import networkx as nx
from data_simulator import simulate_data
from graph_builder import build_graph
from graph_analyzer import analyze_graph
from risk_modeler import simple_risk_propagation, monte_carlo_disruption_simulation

def print_section_header(title):
    print("\n" + "="*80)
    print(f"| {title.upper()}")
    print("="*80)

def main():
    # --- Stage 1: Data Simulation and Graph Building ---
    print_section_header("Stage 1: Data Ingestion & Graph Construction")
    
    raw_data = simulate_data()
    print(f"Raw data items: {len(raw_data)}")
    
    # The build_graph function performs Entity Resolution and Relationship Extraction
    G = build_graph(raw_data)
    
    print(f"\nGraph created successfully! Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    
    print("\n--- Example Node Attributes (Foxconn Facility No. 3) ---")
    foxconn_node = "Foxconn Facility No. 3"
    if G.has_node(foxconn_node):
        print(G.nodes[foxconn_node])
    
    print("\n--- Example Edge (Foxconn -> Sunrise Textiles) ---")
    try:
        edge_data = G.get_edge_data(foxconn_node, "Sunrise Textiles")
        print(list(edge_data.values())[0])
    except:
        print("Edge not found or structure mismatch.")

    # --- Stage 2: Graph Analysis ---
    print_section_header("Stage 2: Graph Analysis (Bottlenecks, Clustering, Traceability)")
    analysis_results = analyze_graph(G)
    
    for key, value in analysis_results.items():
        if isinstance(value, dict):
            print(f"\n[Analysis: {key.replace('_', ' ')}]")
            print(value['Description'])
            if 'Top_Bottlenecks' in value:
                 print(f"  Top Bottlenecks: {[(n, f'{v:.4f}') for n, v in value['Top_Bottlenecks']]}")
            if 'Top_Hubs' in value:
                 print(f"  Top Hubs: {value['Top_Hubs']}")
            if 'Communities' in value:
                 print(f"  Identified Communities: {value['Communities']}")
            if 'Path' in value:
                 print(f"  Shortest Path: {' -> '.join(value['Path'])} (Length: {value['Length']} steps)")
            if 'Suppliers_for_Brand_A' in value:
                 print(f"  Key Upstream Suppliers: {value['Suppliers_for_Brand_A']}")
        else:
            print(f"\n[Analysis: {key.replace('_', ' ')}]\n{value}")


    # --- Stage 3: Risk Propagation Modeling ---
    print_section_header("Stage 3: Risk Propagation Modeling")

    # 3.1 Simple Risk Propagation
    propagated_risk = simple_risk_propagation(G)
    print("\n[3.1] Propagated Risk Score (Simple Model)")
    print("Downstream Risk = Max(Local Risk, Upstream Risk * Propagated Weight)")
    sorted_risk = dict(sorted(propagated_risk.items(), key=lambda item: item[1], reverse=True))
    for node, risk in sorted_risk.items():
        print(f"  - {node}: {risk:.4f} (Base: {G.nodes[node].get('risk_score', 0.0):.2f})")
    
    # 3.2 & 3.3 Monte Carlo Simulation
    print("\n[3.3] Monte Carlo Disruption Simulation (1,000 Iterations)")
    mc_results = monte_carlo_disruption_simulation(G, iterations=1000)

    print(f"  * Local Failure Probabilities (P(local failure)):")
    for node, prob in mc_results['local_failure_probabilities'].items():
        print(f"    - {node}: {prob:.2f}")

    print("\n  * Disruption Probability (P(final failure)) - Simulated:")
    for node, prob in mc_results['disruption_probability_by_node'].items():
        print(f"    - {node}: {prob:.2f}")

    final_prob = mc_results['final_product_disruption_prob']
    print(f"\n==> Final Conclusion: Probability of Brand A DC Disruption: {final_prob:.2%}")
    # 

if __name__ == '__main__':
    # Ensure networkx is available
    try:
        nx.__version__
        main()
    except ImportError:
        print("Error: The 'networkx' library is required to run this project.")
        print("Please install it using: pip install networkx")