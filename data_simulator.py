import random
from typing import List, Dict, Any

def simulate_data() -> List[Dict[str, Any]]:
    """
    Simulates raw, messy data coming from different supply chain sources.
    This data contains naming inconsistencies (for Entity Resolution) and
    unstructured text (for Relationship Extraction).
    """

    # --- Data Source 1: Form Submission (Structured but with variants) ---
    form_data = [
        {"source": "Form", "facility_name": "Foxconn Facility No. 3", "region": "Vietnam", "certification": "OEKO-TEX", "tier": "Tier 2", "relation_text": "Supplies 100% cotton yarn to Sunrise Textiles"},
        {"source": "Form", "facility_name": "Sunrise Textiles", "region": "India", "certification": "GOTS", "tier": "Tier 1", "relation_text": "Delivers finished fabric to Brand A Distribution Center."},
    ]

    # --- Data Source 2: Supplier Excel Upload (Abbreviations/Typos) ---
    excel_data = [
        {"source": "Excel_Upload", "facility_name": "Fxncn 3", "region": "VN", "certification": "OETX", "tier": "Tier 2", "relation_text": "Ships materials to Sunrise Textile India"},
        {"source": "Excel_Upload", "facility_name": "Asia Components Ltd.", "region": "China", "certification": "ISO 9001", "tier": "Tier 3", "relation_text": "Produces circuit boards for FCN3."},
        {"source": "Excel_Upload", "facility_name": "Brand A DC", "region": "US", "certification": "N/A", "tier": "Brand", "relation_text": "Final product assembly."},
    ]

    # --- Data Source 3: Assessment PDF Snippets (Unstructured Text) ---
    # These snippets will be processed for entity and relationship extraction.
    pdf_snippets = [
        {"source": "PDF_Assessment", "text": "The Foxconn Unit 3 in Vietnam is a major producer of components. A recent assessment identified high water stress risk (0.8) due to its location.", "facility_key": "Foxconn Facility No. 3", "risk_type": "Water Stress", "risk_score": 0.8},
        {"source": "PDF_Assessment", "text": "Sunrise Textiles (India) has a moderate water risk (0.78). They hold a 3-month inventory buffer for cotton yarn inputs.", "facility_key": "Sunrise Textiles", "risk_type": "Water Stress", "risk_score": 0.78, "buffer": 3},
        {"source": "PDF_Assessment", "text": "Asia Components uses the boards in 70% of its devices, showing a strong dependency on Facility 3 materials.", "facility_key": "Asia Components Ltd.", "dependency_weight": 0.7},
    ]

    # Combine all data into a single raw list
    raw_data = form_data + excel_data + pdf_snippets
    return raw_data

if __name__ == '__main__':
    data = simulate_data()
    print("--- Sample Raw Input Data ---")
    for item in data[:3]:
        print(item)
    print(f"\nTotal items simulated: {len(data)}")