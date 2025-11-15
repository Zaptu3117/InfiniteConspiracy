# Document Generation Fixes - Complete Summary

## Problem 1: Too Many Technical Documents (60-70% technical)

### Root Cause
Identity node generator (`identity_nodes.py`) was ONLY using technical document types:
- server_log, network_log, firewall_log, vpn_log
- auth_log, login_history, access_control
- badge_log, door_access_log, security_scan
- asset_database, it_inventory, device_registry
- etc.

Since identity chains make up **60% of all subgraphs**, this meant 60%+ of documents were technical.

### Fix Applied
Modified `identity_nodes.py` lines 26-71 to use **75% narrative, 25% technical** mix:

```python
"network": [
    # Narrative (majority)
    "email", "email", "internal_memo", "internal_memo", 
    "incident_report", "security_report",
    # Technical (minority)  
    "server_log", "network_log"
]
```

Applied to all 6 categories: network, auth, physical, system, transaction, mapping.

### Expected Result
- **Before**: 65-70% technical, 30-35% narrative
- **After**: 30-40% technical, 60-70% narrative

---

## Problem 2: Technical Log Arrays in Narrative Documents

### Root Cause
The `_get_expected_fields()` function was telling the LLM to add technical "entries" arrays to narrative documents:

**Line 743 (OLD):**
```python
"diary": '"date": "...", "author": "...", "content": "...", "mood": "...", "entries": [{"time": "...", "text": "..."}]'
```

This caused diaries to have:
- ✅ Good diary content in the `content` field
- ❌ Technical debug logs in the `entries` array like:
  - `[DEBUG] Initializing vector sync module. Status: OK.`
  - `[INFO] Received heartbeat from Node-12A. Latency: 42ms.`
  - `[WARN] Unexpected packet size from Node-7G. Flagging for review.`

### Fix Applied
Removed technical "entries" arrays from narrative document types:

**Lines 743-745 (NEW):**
```python
"diary": '"date": "...", "author": "...", "content": "...", "mood": "..."',

"internal_memo": '"from": "...", "to": "...", "subject": "...", "date": "...", "content": "..."'
```

Also added proper templates for new narrative types (lines 778-788):
- `security_report`
- `incident_report`  
- `it_ticket`
- `hr_memo`
- `personnel_file`
- `audit_report`

### Expected Result
Narrative documents will now have:
- ✅ Pure narrative content (no technical logs mixed in)
- ✅ Appropriate tone and format for each document type
- ✅ Evidence naturally embedded in the story

---

## Document Type Classification

### Narrative Documents (Should NOT have technical log arrays)
- ✅ `email` - Email conversations
- ✅ `diary` - Personal journal entries
- ✅ `internal_memo` - Office memos
- ✅ `security_report` - Security incident narratives
- ✅ `incident_report` - Incident descriptions
- ✅ `it_ticket` - IT support tickets
- ✅ `hr_memo` - HR communications
- ✅ `personnel_file` - Employee records
- ✅ `audit_report` - Audit findings

### Documents with Appropriate Structured Data (CORRECT as-is)
- ✅ `witness_statement` - Has Q&A interview format (not technical logs)
- ✅ `police_report` - Has witness list (not technical logs)
- ✅ `phone_record` - Has call list (appropriate for phone records)

### Technical Documents (SHOULD have log arrays)
- ✅ `server_log`, `firewall_log`, `network_log`, `vpn_log`
- ✅ `badge_log`, `door_access_log`, `access_control`
- ✅ `login_history`, `auth_log`
- ✅ `it_inventory`, `device_registry`, `asset_database`
- ✅ `security_scan`

---

## Files Modified

1. **`backend/src/narrative/conspiracy/nodes/identity_nodes.py`**
   - Lines 26-71: Added narrative document types to all 6 categories
   - Result: 75% narrative, 25% technical distribution

2. **`backend/src/narrative/conspiracy/document_generator.py`**
   - Line 743: Removed `entries` array from `diary`
   - Line 745: Removed `sections` array from `internal_memo`
   - Lines 778-788: Added templates for 6 new narrative document types
   - Result: Narrative documents stay narrative

---

## Testing

Run test to verify document type distribution:
```bash
cd /home/flex3/projects/InvestigationBackEnd/backend
python3 test_doc_types_simple.py
```

Generate a new mystery to test:
```bash
cd /home/flex3/projects/InvestigationBackEnd
uv run python main.py
```

Expected output in `backend/outputs/conspiracies/[mystery_name]/documents/`:
- 60-70% narrative documents (emails, memos, reports, diaries, statements)
- 30-40% technical documents (logs, databases)
- NO technical log arrays in narrative documents

---

## Key Insight

The system had **TWO separate but related problems**:

1. **Document Type Selection**: Identity nodes only chose technical types → Fixed by expanding type options
2. **Document Content Generation**: Even when narrative types were chosen, technical logs were added → Fixed by removing log arrays from narrative templates

Both fixes were necessary to achieve properly narrative documents.

