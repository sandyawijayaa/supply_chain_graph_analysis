import networkx as nx
from typing import List, Dict, Any, Tuple, Union 
import re
import difflib

# --- MOCK NLP/EMBEDDING CONFIGURATION ---
SIMILARITY_MAP = {
    "Fxncn 3": "Foxconn Facility No. 3",
    "Foxconn Unit 3": "Foxconn Facility No. 3",
    "Sunrise Textile India": "Sunrise Textiles",
    "Brand A DC": "Brand A Distribution Center",
    "OETX": "OEKO-TEX",
    "VN": "Vietnam",
    "FCN3": "Foxconn Facility No. 3",
}

RELATION_MAP = {
    "Supplies": "SUPPLIES",
    "Delivers": "SUPPLIES",
    "Ships materials": "SUPPLIES",
    "Produces": "PRODUCES",
    "assembly": "FINAL_ASSEMBLY",
}

# --- Helper function for consistent node initialization ---
def _initialize_node_attributes(node_id: int, canonical_name: str) -> Dict[str, Any]:
    """Provides a consistent set of default attributes for any new Facility node."""
    return {
        "label": "Facility",
        "id": f"fac_{node_id}",
        "name": canonical_name,
        "certifications": set(), # MUST be initialized as a set
        "tier": None,
        "region": None,
        "risk_score": 0.0,
        "dependency_weight": 1.0, 
        "inventory_buffer": 0,
    }
# --- End Helper function ---

def _preprocess_name(name: str) -> str:
    """Preprocess name: lower, strip punc, expand common abbs (simulated)."""
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name) # strip punctuation
    for abbr, expanded in SIMILARITY_MAP.items():
        name = name.replace(abbr.lower(), expanded.lower())
    return name

def resolve_entity(name: str) -> str:
    """
    Simulates the Entity Resolution process.
    """
    processed_name = _preprocess_name(name)

    canonical_names = set(SIMILARITY_MAP.values())
    
    # 1. Check for exact match or known alias
    for alias, canonical in SIMILARITY_MAP.items():
        if name.strip() == alias:
            return canonical
        if processed_name in _preprocess_name(alias):
             return canonical

    # 2. Use fuzzy matching against canonical names
    closest_match = difflib.get_close_matches(name.strip(), list(canonical_names), n=1, cutoff=0.8)
    if closest_match:
        return closest_match[0]

    # 3. If no match, the name itself becomes the canonical name
    return name.strip()


def extract_relations(text: str) -> Union[Tuple[str, str, str], None]:
    """
    Simulates Relationship Extraction (RE) using improved rule-based logic
    to accurately isolate the target facility name.
    """
    text_lower = text.lower()
    
    # Pattern 1: Look for "to [TARGET_NAME]" or "for [TARGET_NAME]"
    match_to = re.search(r'(to|for)\s+([\w\s\.]+)', text_lower)
    
    if match_to:
        # Capture the destination entity name (everything after 'to' or 'for')
        raw_object_name = match_to.group(2).strip()
        
        # Isolate the name before any ending punctuation
        target_name = resolve_entity(raw_object_name.split('.')[0].strip())
        
        # Identify the relation type based on surrounding verbs
        rel_type = "UNKNOWN_RELATION"
        for phrase, r_type in RELATION_MAP.items():
            if phrase.lower() in text_lower:
                rel_type = r_type
                break

        # Extract Material: Everything between the first recognized verb and the preposition 'to/for'
        material_match = re.search(r'(supplies|delivers|ships|produces)\s+(.*?)\s+(to|for)', text_lower)
        material = material_match.group(2).strip() if material_match and material_match.group(2) else "UNKNOWN MATERIAL"

        if material == "":
             material = "UNKNOWN MATERIAL"
        
        return rel_type, target_name, material
        
    # Handle the special case where relation_text is only an attribute, not an edge
    if "final product assembly" in text_lower:
        return None 

    return None

def build_graph(raw_data: List[Dict[str, Any]]) -> nx.MultiDiGraph:
    """
    Processes raw data, performs ER/RE, and builds the NetworkX graph.
    """
    G = nx.MultiDiGraph()
    facility_nodes = {} # Used for generating unique IDs

    # 1. Create Nodes and Add Attributes
    for item in raw_data:
        raw_name = item.get("facility_name") or item.get("facility_key")
        
        if raw_name:
            # Entity Resolution
            canonical_name = resolve_entity(raw_name)

            # A. Explicit Node Creation (First time we see the entity)
            if canonical_name not in G:
                node_id_counter = len(facility_nodes) + 1
                facility_nodes[canonical_name] = node_id_counter
                
                # Use the helper function for consistent initialization
                attributes = _initialize_node_attributes(node_id_counter, canonical_name)
                G.add_node(canonical_name, **attributes)
            
            # B. Attribute Aggregation (Regardless of whether it was just created or already existed)
            node_data = G.nodes[canonical_name]
            
            # Certifications (Add to the set)
            cert = item.get("certification")
            if cert:
                node_data['certifications'].add(resolve_entity(cert))

            # Other simple attributes (Overwrites with most recent data)
            if item.get("tier"):
                node_data['tier'] = item["tier"]
            if item.get("region"):
                node_data['region'] = resolve_entity(item["region"])

            # Risk/Dependency attributes
            if item.get("risk_score") is not None:
                 node_data['risk_score'] = item["risk_score"]
            if item.get("dependency_weight") is not None:
                 node_data['dependency_weight'] = item["dependency_weight"]
            if item.get("buffer") is not None:
                 node_data['inventory_buffer'] = item["buffer"]
            
            # 2. Extract and Create Edges
            relation_text = item.get("relation_text")
            if relation_text:
                relation_result = extract_relations(relation_text)
                if relation_result:
                    rel_type, target_name, material = relation_result
                    
                    # Ensure target node exists (Resolve the target name)
                    resolved_target_name = resolve_entity(target_name)
                    
                    # C. Implicit Node Creation (Target of an edge not seen before)
                    if resolved_target_name not in G:
                        node_id_counter = len(facility_nodes) + 1
                        facility_nodes[resolved_target_name] = node_id_counter
                        
                        # MUST use the same initialization for consistency
                        attributes = _initialize_node_attributes(node_id_counter, resolved_target_name)
                        G.add_node(resolved_target_name, **attributes)

                    # Create the edge
                    G.add_edge(
                        canonical_name, 
                        resolved_target_name,    
                        relation=rel_type,
                        material=material,
                        weight=1.0 
                    )
    
    # Final cleanup of attributes (convert sets back to list for cleaner output)
    for node, data in G.nodes(data=True):
        if 'certifications' in data:
            data['certifications'] = list(data['certifications'])

    return G