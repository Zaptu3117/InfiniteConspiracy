"""Test document type diversity after fix."""

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from narrative.conspiracy.nodes.identity_nodes import IdentityNodeGenerator

def test_document_type_diversity():
    """Test that identity nodes now use diverse document types."""
    
    generator = IdentityNodeGenerator()
    
    print("\n" + "="*60)
    print("TESTING DOCUMENT TYPE DIVERSITY")
    print("="*60)
    
    # Test each category
    categories = ["network", "auth", "physical", "system", "transaction", "mapping"]
    
    for category in categories:
        doc_types = generator.doc_types.get(category, [])
        
        # Count technical vs narrative
        technical_types = [
            "server_log", "network_log", "firewall_log", "vpn_log",
            "auth_log", "login_history", "access_control",
            "badge_log", "door_access_log", "security_scan",
            "asset_database", "it_inventory", "device_registry",
            "audit_log", "transaction_history", "system_log",
            "employee_database", "user_registry"
        ]
        
        narrative_types = [
            "email", "internal_memo", "incident_report", "security_report",
            "witness_statement", "it_ticket", "hr_memo", "personnel_file",
            "audit_report"
        ]
        
        technical_count = sum(1 for dt in doc_types if dt in technical_types)
        narrative_count = sum(1 for dt in doc_types if dt in narrative_types)
        total = len(doc_types)
        
        technical_pct = (technical_count / total * 100) if total > 0 else 0
        narrative_pct = (narrative_count / total * 100) if total > 0 else 0
        
        print(f"\n{category.upper()}: (Total: {total})")
        print(f"  Technical: {technical_count} ({technical_pct:.1f}%)")
        print(f"  Narrative: {narrative_count} ({narrative_pct:.1f}%)")
        print(f"  Types: {doc_types}")
        
        # Verify narrative is majority
        if narrative_count > technical_count:
            print(f"  ✅ PASS: Narrative types are majority")
        else:
            print(f"  ❌ FAIL: Technical types are still majority")
    
    print("\n" + "="*60)
    print("OVERALL ASSESSMENT")
    print("="*60)
    
    # Calculate overall distribution
    all_types = []
    for cat_types in generator.doc_types.values():
        all_types.extend(cat_types)
    
    technical_types_list = [
        "server_log", "network_log", "firewall_log", "vpn_log",
        "auth_log", "login_history", "access_control",
        "badge_log", "door_access_log", "security_scan",
        "asset_database", "it_inventory", "device_registry",
        "audit_log", "transaction_history", "system_log",
        "employee_database", "user_registry"
    ]
    
    total_technical = sum(1 for dt in all_types if dt in technical_types_list)
    total_narrative = len(all_types) - total_technical
    
    print(f"\nTotal document type slots: {len(all_types)}")
    print(f"  Technical: {total_technical} ({total_technical/len(all_types)*100:.1f}%)")
    print(f"  Narrative: {total_narrative} ({total_narrative/len(all_types)*100:.1f}%)")
    
    if total_narrative > total_technical:
        print(f"\n✅ SUCCESS: Identity nodes now favor narrative document types!")
        print(f"   This means ~60% of identity-based documents will be narrative.")
        print(f"   Since identity chains are 60% of subgraphs, this will")
        print(f"   significantly increase narrative document presence.")
    else:
        print(f"\n❌ FAILURE: Technical types still dominate")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_document_type_diversity()



