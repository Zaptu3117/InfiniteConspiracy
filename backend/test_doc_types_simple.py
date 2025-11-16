"""Simple test to show document type distribution."""

# Recreate the doc_types dictionary from identity_nodes.py
doc_types = {
    "network": [
        # Narrative (majority)
        "email", "email", "internal_memo", "internal_memo", 
        "incident_report", "security_report",
        # Technical (minority)  
        "server_log", "network_log"
    ],
    "auth": [
        # Narrative (majority)
        "email", "email", "internal_memo", "security_report",
        "witness_statement", "incident_report",
        # Technical (minority)
        "login_history", "auth_log"
    ],
    "physical": [
        # Narrative (majority)
        "security_report", "security_report", "witness_statement",
        "internal_memo", "incident_report", "email",
        # Technical (minority)
        "badge_log", "door_access_log"
    ],
    "system": [
        # Narrative (majority)
        "email", "email", "internal_memo", "internal_memo",
        "incident_report", "it_ticket",
        # Technical (minority)
        "it_inventory", "asset_database"
    ],
    "transaction": [
        # Narrative (majority)
        "email", "internal_memo", "internal_memo", 
        "audit_report", "incident_report",
        # Technical (minority)
        "audit_log", "transaction_history"
    ],
    "mapping": [
        # Narrative (majority)
        "email", "internal_memo", "internal_memo",
        "hr_memo", "personnel_file", "witness_statement",
        # Technical (minority)
        "employee_database", "user_registry"
    ]
}

print("\n" + "="*70)
print("DOCUMENT TYPE DIVERSITY TEST - IDENTITY NODES")
print("="*70)

technical_types = {
    "server_log", "network_log", "firewall_log", "vpn_log",
    "auth_log", "login_history", "access_control",
    "badge_log", "door_access_log", "security_scan",
    "asset_database", "it_inventory", "device_registry",
    "audit_log", "transaction_history", "system_log",
    "employee_database", "user_registry"
}

narrative_types = {
    "email", "internal_memo", "incident_report", "security_report",
    "witness_statement", "it_ticket", "hr_memo", "personnel_file",
    "audit_report", "diary"
}

all_types = []
for category, types in doc_types.items():
    all_types.extend(types)
    
    tech_count = sum(1 for t in types if t in technical_types)
    narr_count = sum(1 for t in types if t in narrative_types)
    total = len(types)
    
    print(f"\n{category.upper()}:")
    print(f"  Total: {total} | Technical: {tech_count} ({tech_count/total*100:.0f}%) | Narrative: {narr_count} ({narr_count/total*100:.0f}%)")
    print(f"  Types: {types}")

print("\n" + "="*70)
print("OVERALL DISTRIBUTION")
print("="*70)

total_tech = sum(1 for t in all_types if t in technical_types)
total_narr = sum(1 for t in all_types if t in narrative_types)
total = len(all_types)

print(f"\nTotal slots: {total}")
print(f"Technical: {total_tech} ({total_tech/total*100:.1f}%)")
print(f"Narrative: {total_narr} ({total_narr/total*100:.1f}%)")

print("\n" + "="*70)
print("IMPACT ANALYSIS")
print("="*70)

print(f"\n✅ Identity chains make up 60% of all subgraphs")
print(f"✅ Identity nodes now use {total_narr/total*100:.0f}% narrative document types")
print(f"✅ This means ~{60 * (total_narr/total):.0f}% of ALL documents will be narrative")
print(f"\nExpected document distribution in generated mystery:")
print(f"  - Narrative: ~60-70% (emails, memos, reports, statements)")
print(f"  - Technical: ~30-40% (logs, databases)")

print("\n" + "="*70)


