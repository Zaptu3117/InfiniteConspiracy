# Document Type Diversity Fix

## Problem Identified

Your conspiracy mystery generation was producing **too many technical documents** (logs, databases) and **not enough narrative documents** (emails, memos, reports, diaries).

### Root Cause

The issue was in `/backend/src/narrative/conspiracy/nodes/identity_nodes.py`:

**Identity chains** (which make up **60% of all subgraphs**) were ONLY using technical document types:
- server_log, network_log, firewall_log, vpn_log
- auth_log, login_history, access_control  
- badge_log, door_access_log, security_scan
- asset_database, it_inventory, device_registry
- audit_log, transaction_history, system_log
- employee_database, user_registry

Since 60% of subgraphs are identity-based, this meant **60%+ of all documents were technical**.

## Solution Implemented

### 1. Updated Identity Node Document Types

Modified `identity_nodes.py` to use a **75% narrative, 25% technical** mix for each category:

**Example - Network category:**
```python
"network": [
    # Narrative (majority)
    "email", "email", "internal_memo", "internal_memo", 
    "incident_report", "security_report",
    # Technical (minority)  
    "server_log", "network_log"
]
```

Applied this pattern to all 6 categories: network, auth, physical, system, transaction, mapping.

### 2. Added Missing Document Type Instructions

Added formatting instructions in `document_generator.py` for new narrative types:
- `security_report` - Professional security incident reports
- `incident_report` - General incident documentation
- `it_ticket` - IT support tickets with comments/resolution
- `hr_memo` - HR communications  
- `personnel_file` - Employee records with performance notes
- `audit_report` - Formal audit findings

## Expected Results

### Before Fix
- **Technical documents**: ~65-70%
- **Narrative documents**: ~30-35%

### After Fix  
- **Technical documents**: ~30-40%
- **Narrative documents**: ~60-70%

### Document Type Breakdown (After Fix)

The new distribution will include:
- **Emails**: ~20-25% of documents
- **Internal Memos**: ~15-20% of documents
- **Incident/Security Reports**: ~10-15% of documents
- **Witness Statements**: ~5-8% of documents
- **IT Tickets**: ~3-5% of documents
- **HR Memos/Personnel Files**: ~3-5% of documents
- **Audit Reports**: ~2-4% of documents
- **Diaries**: ~2-3% of documents
- **Technical Logs**: ~20-30% of documents (server, network, firewall, VPN, etc.)
- **Database Records**: ~5-10% of documents

## Files Modified

1. **`backend/src/narrative/conspiracy/nodes/identity_nodes.py`**
   - Lines 26-71: Replaced technical-only doc_types with narrative-majority mix

2. **`backend/src/narrative/conspiracy/document_generator.py`**
   - Lines 295-426: Added 6 new document type instruction blocks

## Testing

Run this command to see the new distribution:
```bash
cd /home/flex3/projects/InvestigationBackEnd/backend
python3 test_doc_types_simple.py
```

## Next Steps

To verify the fix works in a full generation:

```bash
cd /home/flex3/projects/InvestigationBackEnd
uv run python main.py
```

Then check the `backend/outputs/conspiracies/[mystery_name]/documents/` folder. You should now see:
- Many more `*.json` files with email/memo/report content
- Much better narrative flow
- Technical logs only where appropriate for identity chain evidence

## Impact

This fix directly addresses your concern: **"Why do we only have technical documents and no emails or other narrative docs?"**

The answer was that identity node generation (60% of evidence) was hard-coded to only use technical document types. Now it favors narrative types, resulting in a much more engaging and readable mystery with proper story documents.

