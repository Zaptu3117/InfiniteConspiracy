"""Test that narrative documents don't have technical log contamination."""

import sys
import json
sys.path.insert(0, '/home/flex3/projects/InvestigationBackEnd/backend/src')

def test_document_contamination():
    """Check recent generated documents for contamination."""
    
    import os
    import glob
    
    # Find most recent conspiracy output
    conspiracy_dirs = glob.glob('/home/flex3/projects/InvestigationBackEnd/backend/outputs/conspiracies/*')
    if not conspiracy_dirs:
        print("No conspiracy outputs found")
        return
    
    latest_dir = max(conspiracy_dirs, key=os.path.getmtime)
    doc_dir = os.path.join(latest_dir, 'documents')
    
    if not os.path.exists(doc_dir):
        print(f"No documents directory in {latest_dir}")
        return
    
    print(f"\n{'='*80}")
    print(f"CHECKING DOCUMENTS IN: {os.path.basename(latest_dir)}")
    print(f"{'='*80}\n")
    
    # Define narrative document types
    narrative_types = ["email", "diary", "internal_memo", "security_report", 
                      "incident_report", "it_ticket", "hr_memo", "personnel_file",
                      "audit_report"]
    
    # Fields that indicate technical contamination
    contamination_fields = ["entries", "logs", "system_logs", "authentication_events",
                           "sections", "diaries", "emails", "system_events"]
    
    total_narrative = 0
    contaminated = 0
    clean = 0
    
    for doc_file in sorted(os.listdir(doc_dir)):
        if not doc_file.endswith('.json'):
            continue
            
        doc_path = os.path.join(doc_dir, doc_file)
        
        try:
            with open(doc_path, 'r') as f:
                doc = json.load(f)
            
            doc_type = doc.get('document_type', 'unknown')
            
            # Only check narrative documents
            if doc_type not in narrative_types:
                continue
            
            total_narrative += 1
            fields = doc.get('fields', {})
            
            # Check for contamination
            found_contamination = []
            for bad_field in contamination_fields:
                if bad_field in fields:
                    found_contamination.append(bad_field)
                # Also check top level
                if bad_field in doc:
                    found_contamination.append(f"top-level:{bad_field}")
            
            if found_contamination:
                contaminated += 1
                print(f"❌ CONTAMINATED: {doc_file}")
                print(f"   Type: {doc_type}")
                print(f"   Bad fields: {', '.join(found_contamination)}")
                print(f"   All fields: {list(fields.keys())}")
                print()
            else:
                clean += 1
                print(f"✅ CLEAN: {doc_file}")
                print(f"   Type: {doc_type}")
                print(f"   Fields: {list(fields.keys())}")
                print()
        
        except Exception as e:
            print(f"⚠️  Error reading {doc_file}: {e}")
            print()
    
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total narrative documents: {total_narrative}")
    print(f"✅ Clean: {clean} ({clean/total_narrative*100 if total_narrative > 0 else 0:.1f}%)")
    print(f"❌ Contaminated: {contaminated} ({contaminated/total_narrative*100 if total_narrative > 0 else 0:.1f}%)")
    print()
    
    if contaminated == 0 and total_narrative > 0:
        print("🎉 SUCCESS! All narrative documents are clean!")
    elif contaminated > 0:
        print(f"⚠️  FAILED! {contaminated} documents still have technical log contamination")
    else:
        print("⚠️  No narrative documents found to test")
    
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_document_contamination()

