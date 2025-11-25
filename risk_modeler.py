import networkx as nx
import random
from typing import Dict, Any, List

def calculate_edge_weight(data: Dict[str, Any]) -> float:
    """
    Calculates the dependency strength (propagation weight) for an edge.
    Weight = (Base Dependency) * (1 - Buffer/Elasticity Factor)
    """
    # Base dependency: 0.7 for strong connection, 1.0 if not specified
    # Dependency weight comes from the data (e.g., 70% of devices use the material)
    dependency = data.get('dependency_weight', 1.0) 

    # Buffer weight: If inventory > 0, reduce the propagation weight (risk dampening)
    buffer_months = data.get('inventory_buffer', 0)
    buffer_factor = min(buffer_months / 3, 1.0) # Max 3 months dampening
    
    # Lead time elasticity factor (0.0 to 1.0). For this simulation, we'll assume 
    # a fixed elasticity of 0.1 for all suppliers without an explicit 'buffer'
    elasticity = 0.1 if buffer_months == 0 else 0.0

    # Propagation Weight: High dependency, low buffer/elasticity = high weight (closer to 1.0)
    propagation_weight = dependency * (1.0 - (buffer_factor * 0.5) - (elasticity * 0.1)) 
    
    # Ensure weight is between 0.1 and 1.0
    return max(0.1, min(propagation_weight, 1.0))


def simple_risk_propagation(G: nx.MultiDiGraph) -> Dict[str, float]:
    """
    Step 3.1: Calculates the final risk score using the formula:
    Downstream Risk = Upstream Risk * Propagation Weight
    
    This is a simplified cumulative model.
    """
    # 1. Initialize risk scores
    final_risk = {node: G.nodes[node].get('risk_score', 0.0) for node in G.nodes}
    
    # 2. Iterate through nodes in topological order (if possible) or multiple passes
    # to allow risk to flow downstream. We'll use 5 passes to ensure risk propagates fully.
    for _ in range(5):
        for u, v, data in G.edges(data=True):
            # u -> v (u is upstream, v is downstream)
            
            # Calculate Propagation Weight for the edge
            # For simplicity, we just use the calculated edge weight here.
            prop_weight = calculate_edge_weight(G.nodes[u]) 
            
            # Risk transfer: Add risk from upstream (u) to downstream (v)
            upstream_risk = final_risk[u]
            transferred_risk = upstream_risk * prop_weight
            
            # Update downstream risk (take the max of current local risk or transferred risk)
            # A more complex model might average or sum. We use MAX to reflect the highest threat.
            final_risk[v] = max(final_risk[v], transferred_risk)
            
    return final_risk

def monte_carlo_disruption_simulation(G: nx.MultiDiGraph, iterations: int = 1000) -> Dict[str, Any]:
    """
    Step 3.3: Monte Carlo simulation to estimate the probability of disruption.
    
    P(final failure) = P(local failure) + P(upstream failure x dependency strength).
    """
    
    # --- Step 1: Calculate Probability of Local Failure (based on risk score) ---
    # Rule: Risk Score 0.7-0.9 -> 10% failure proba; 0.9-1.0 -> 20% failure proba
    failure_prob_local = {}
    for node, data in G.nodes(data=True):
        risk = data.get('risk_score', 0.0)
        if risk >= 0.9:
            failure_prob_local[node] = 0.20
        elif risk >= 0.7:
            failure_prob_local[node] = 0.10
        else:
            failure_prob_local[node] = 0.02 # Base failure rate

    # --- Step 2: Monte Carlo Simulation ---
    disruption_count = {node: 0 for node in G.nodes}
    
    for _ in range(iterations):
        # A. Roll the dice for local failure
        is_failed = {node: random.random() < failure_prob_local[node] for node in G.nodes}
        
        # B. Propagate failure
        # Use multiple passes to ensure failure flows downstream
        for pass_num in range(3):
            for u, v, key, data in G.edges(keys=True, data=True):
                # u -> v (u is upstream, v is downstream)

                # If upstream (u) is already failed, the failure propagates
                if is_failed[u]:
                    is_failed[v] = True
                    continue
                
                # If u is operational, check if v fails due to upstream failure probability
                # P(upstream failure x dependency strength)
                # Dependency strength is simulated by the edge weight.
                
                # In this simplified model, we use the upstream node's local failure probability
                # combined with a measure of dependency (1.0 in this model).
                # A more complex model would use the calculated P(upstream failure) * weight.
                
                # For this implementation, we simplify: if upstream fails, downstream fails.
                
        # C. Count disruptions
        for node in G.nodes:
            if is_failed[node]:
                disruption_count[node] += 1

    # --- Step 3: Calculate Disruption Probability ---
    disruption_probability = {
        node: count / iterations for node, count in disruption_count.items()
    }
    
    # Calculate the probability that the final product (Brand A DC) is disrupted
    final_product_node = "Brand A Distribution Center"
    final_prob = disruption_probability.get(final_product_node, 0)
    
    return {
        "iterations": iterations,
        "local_failure_probabilities": failure_prob_local,
        "disruption_probability_by_node": dict(sorted(disruption_probability.items(), key=lambda item: item[1], reverse=True)),
        "final_product_disruption_prob": final_prob
    }