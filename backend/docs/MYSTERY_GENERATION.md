# Mystery Generation Guide

Comprehensive guide to mystery generation in Infinite Conspiracy.

## Overview

The backend supports two mystery generation pipelines:

1. **LLM Narrative Pipeline** - Traditional detective mysteries
2. **Conspiracy Pipeline** - Advanced conspiracy-themed mysteries

Both pipelines create mysteries with multi-hop reasoning requirements that resist automation.

## LLM Narrative Pipeline

**File**: `src/narrative/pipeline.py`

### Pipeline Steps

The LLM pipeline follows a 7-step process:

```
Step -1: Premise Generation (question + answer)
   ↓
Step 0: Proof Tree Generation (reasoning steps)
   ↓
Step 1: Character Generation (5-10 characters)
   ↓
Step 2: Timeline Generation (3-14 days)
   ↓
Step 3: Location Generation (3-8 locations)
   ↓
Step 4: Document Planning (20-25 documents)
   ↓
Step 5: Graph Assembly (cross-references)
   ↓
Document Generation (parallel async)
   ↓
Cryptography (optional)
   ↓
Red Herrings (optional)
   ↓
Image Generation (optional)
   ↓
Validation
```

### Step Details

#### Step -1: Premise Generation

Generates the core question and answer using LLM.

**Input**: Difficulty level  
**Output**: Question string, Answer string

**Example**:
```
Question: "Who leaked the classified documents to the press?"
Answer: "Sarah Martinez"
```

#### Step 0: Proof Tree

Creates a reasoning tree with 3-7 hops.

**Structure**:
```python
{
  "answer": "Sarah Martinez",
  "inference_nodes": [
    {
      "node_id": "node_1",
      "inference": "Email mentions meeting at 02:47am",
      "document_ids": ["doc_1_email"],
      "reasoning_type": "direct_observation",
      "parent_nodes": [],
      "children_nodes": ["node_3"]
    },
    # ... more nodes ...
  ],
  "total_hops": 4,
  "min_hops": 3
}
```

#### Step 1: Characters

Generates 5-10 characters with:
- Full names
- Roles/professions
- Relationships
- Personalities

**Example**:
```python
{
  "name": "Sarah Martinez",
  "role": "Senior Systems Administrator",
  "age": 34,
  "personality": "Meticulous, private, technically skilled",
  "relationships": ["colleague of John Doe", "reports to Mike Chen"]
}
```

#### Step 2: Timeline

Creates a timeline spanning 3-14 days with key events.

**Example**:
```python
{
  "start_date": "2024-11-10",
  "end_date": "2024-11-13",
  "events": [
    {
      "timestamp": "2024-11-12T18:30:00Z",
      "description": "Email sent planning meeting",
      "characters": ["John Doe"],
      "location": "Office"
    },
    # ... more events ...
  ]
}
```

#### Step 3: Locations

Generates 3-8 locations relevant to the mystery.

**Example**:
```python
{
  "name": "Warehouse 4B",
  "type": "industrial",
  "description": "Secure storage facility for classified materials",
  "access_level": "restricted"
}
```

#### Step 4: Document Planning

Plans which documents to create and what evidence each contains.

**Example**:
```python
{
  "document_id": "doc_1_email",
  "document_type": "email",
  "from_character": "John Doe",
  "to_characters": ["Operations Team"],
  "contains_clues": ["meeting_time", "location_reference"],
  "proof_step": 1
}
```

#### Step 5: Graph Assembly

Connects all narrative elements into a coherent graph structure.

**Output**: NarrativeGraph object with all relationships

### Usage

```python
from narrative.pipeline import LLMNarrativePipeline
from utils.llm_clients import CerebrasClient

# Initialize
cerebras = CerebrasClient(api_key)
pipeline = LLMNarrativePipeline(
    cerebras,
    config,
    replicate_token=replicate_token,
    openai_key=openai_key
)

# Generate
mystery = await pipeline.generate_mystery_with_llm(
    difficulty=7,
    num_docs=20
)

# Save
mystery_path = mystery.save_to_file("outputs/mysteries")
```

## Conspiracy Pipeline

**File**: `src/narrative/conspiracy/conspiracy_pipeline.py`

### Pipeline Steps

The conspiracy pipeline creates more complex mysteries:

```
Phase 1: Political Context Generation
   ↓
Phase 2: Conspiracy Premise (WHO, WHAT, WHY, HOW)
   ↓
Phase 3: Answer Template Extraction
   ↓
Phase 4: Sub-Graph Generation
   ├─ Identity chains (technical)
   ├─ Psychological chains (behavioral)
   └─ Cryptographic chains (encrypted)
   ↓
Phase 5: Evidence Node Generation
   ↓
Phase 6: Document-SubGraph Mapping
   ↓
Phase 7: Document Generation
   ↓
Phase 8: Character Enhancement
   ↓
Phase 9: Phrase Encryption
   ↓
Phase 10: Image Clue Mapping
   ↓
Phase 11: Red Herring Integration
   ↓
Phase 12: Validation
```

### Key Differences from LLM Pipeline

| Feature | LLM Pipeline | Conspiracy Pipeline |
|---------|-------------|-------------------|
| **Answer Format** | Single string | 4 dimensions (WHO/WHAT/WHY/HOW) |
| **Political Context** | No | Yes (shadow organizations) |
| **Evidence Chains** | Single proof tree | Multiple sub-graphs |
| **Identity Clues** | LLM-generated | Programmatically guaranteed |
| **Crypto System** | Simple keys | Inference-based keys |
| **Red Herrings** | Optional add-on | Integrated as broken chains |

### Four-Dimensional Answers

Conspiracy mysteries require answering 4 questions:

1. **WHO** - Which conspirator(s)?
2. **WHAT** - What operation/goal?
3. **WHY** - What motivation?
4. **HOW** - How was it executed?

**Example**:
```
WHO: "Director Elara Voss"
WHAT: "Operation Eclipse Veil"
WHY: "Resurrect ancient cult influence"
HOW: "Infiltrate government archives to obtain forbidden texts"
```

### Evidence Sub-Graphs

The conspiracy pipeline generates multiple independent evidence chains:

**Types**:
- **Identity Chains (60%)**: Technical identifiers (IPs, badges, IDs)
- **Psychological Chains (20%)**: Behavioral patterns, relationships
- **Cryptographic Chains (20%)**: Encrypted communications
- **Red Herrings (20-30%)**: Broken/misleading chains

**Structure**:
```python
{
  "subgraph_id": "sg_identity_001",
  "chain_type": "identity",
  "target_answer_dimension": "WHO",
  "nodes": [
    {
      "node_id": "node_1",
      "inference": "Badge 4217 accessed Warehouse 4B",
      "evidence_type": "badge_number",
      "technical_details": {"badge": "4217", "location": "Warehouse 4B"}
    },
    {
      "node_id": "node_2",
      "inference": "Badge 4217 belongs to Sarah Martinez",
      "evidence_type": "employee_record",
      "technical_details": {"badge": "4217", "employee": "Sarah Martinez"}
    }
  ],
  "is_complete": true,
  "is_red_herring": false
}
```

### Usage

```python
from narrative.conspiracy.conspiracy_pipeline import ConspiracyPipeline
from utils.llm_clients import CerebrasClient

# Initialize
cerebras = CerebrasClient(api_key)
pipeline = ConspiracyPipeline(
    cerebras,
    config,
    replicate_token=replicate_token
)

# Generate
conspiracy = await pipeline.generate_conspiracy_mystery(
    difficulty=8,
    num_documents=25,
    conspiracy_type="occult"  # or "secret_society", "underground_network"
)

# Save
conspiracy_path = conspiracy.save_to_file("outputs/conspiracies")
```

## Document Generation

**Location**: `src/narrative/document_gen/`

Both pipelines use the same document generation system.

### Parallel Generation

Documents are generated in parallel for 10x speedup:

```python
# Instead of:
for doc_plan in doc_plans:
    doc = await generate_document(doc_plan)  # Sequential

# We do:
tasks = [generate_document(plan) for plan in doc_plans]
documents = await asyncio.gather(*tasks)  # Parallel
```

### Document Types

12+ document types are supported:

| Type | Description | Example Use |
|------|-------------|-------------|
| `email` | Email correspondence | Communication evidence |
| `network_log` | Network activity | IP addresses, connections |
| `badge_log` | Physical access | Entry/exit times |
| `surveillance_log` | Security records | Events, observations |
| `police_report` | Official reports | Incidents, testimonies |
| `diary` | Personal journal | Thoughts, confessions |
| `internal_memo` | Company memos | Announcements, directives |
| `medical_record` | Health records | Diagnoses, treatments |
| `financial_statement` | Financial data | Transactions, balances |
| `newspaper` | News articles | Public information |
| `technical_manual` | Documentation | Equipment, procedures |
| `chat_transcript` | IM logs | Conversations |

### Document Structure

All documents follow a standard JSON structure:

```json
{
  "document_id": "doc_5_email",
  "document_type": "email",
  "fields": {
    "from": "john@company.com",
    "to": ["sarah@company.com"],
    "subject": "Meeting Notes",
    "body": "We need to meet at 02:47am...",
    "timestamp": "2024-11-13T02:30:00Z"
  },
  "cipher_info": {
    "encrypted": true,
    "cipher_type": "caesar",
    "encrypted_sections": ["body"],
    "hint": "Check badge logs for key"
  },
  "contains_clues": ["meeting_time", "location_hint"],
  "proof_step": 1
}
```

## Cryptography Integration

**File**: `src/narrative/crypto_integrator.py`

### Cipher Types

#### Caesar Cipher
- Shift-based encryption
- Numeric key (0-25)
- Key hidden in documents or images

**Example**:
```
Plaintext: "MEET AT WAREHOUSE"
Key: 13
Ciphertext: "ZRRG NG JNERFUBHFR"
```

#### Vigenère Cipher
- Keyword-based encryption
- Key scattered across 3+ documents
- More complex than Caesar

**Example**:
```
Plaintext: "MEET AT WAREHOUSE"
Key: "SECRET"
Ciphertext: "OIIX EX MIKVWLSYI"
```

### Key Distribution

Keys are strategically placed:

```python
# Document A contains encrypted text
doc_a = {
  "body": "Zrrg ng jnerfubhfr...",  # Encrypted
  "cipher_info": {
    "hint": "Check the badge log for the shift value"
  }
}

# Document B contains the key
doc_b = {
  "badge_entries": [
    {"badge_number": "4217", ...},  # This is the key!
    {"badge_number": "5829", ...}
  ]
}
```

## Red Herrings

**File**: `src/narrative/red_herrings.py`

### Types

1. **Similar Names**: John Smith vs John Smythe
2. **Misleading Locations**: Near but wrong
3. **Contradictory Timestamps**: Off by hours
4. **False Relationships**: Alleged connections
5. **Suspicious but Innocent**: Red herring actions

### Integration

Red herrings are subtly woven into documents:

```python
# Real clue
"Sarah Martinez accessed Warehouse 4B at 02:43am"

# Red herring
"John Smythe was seen near Warehouse 3A around 02:30am"
# (Similar name, wrong location, wrong time)
```

## Image Generation

**File**: `src/images/generator.py`

### Process

1. Generate prompt from document context
2. Call Replicate API (Flux model)
3. Validate with GPT-4V
4. Retry if validation fails
5. Save image file

### Visual Clues

Images can contain:
- Badge numbers
- License plates
- Document headers
- Timestamps
- Location markers

**Example**:
```python
{
  "image_id": "img_badge_001",
  "description": "Security badge photo showing number 4217",
  "required_elements": ["badge_number_4217", "sarah_martinez_name"],
  "validation_result": {
    "contains_badge_number": true,
    "badge_number_visible": "4217",
    "confidence": 0.95
  }
}
```

## Validation

**File**: `src/validation/conspiracy_validator.py`

### Tests

#### 1. Single-LLM Test (Must Fail)

Give all documents to LLM in one call. It should NOT solve the mystery.

```python
prompt = f"""
All documents: {all_documents}
Question: {question}
Answer:
"""

response = llm.generate(prompt)

# This should fail
assert response != correct_answer
```

#### 2. Multi-Hop Test (Must Succeed)

Guide LLM step-by-step. It SHOULD solve the mystery.

```python
for step in proof_tree.steps:
    prompt = f"""
    Documents so far: {relevant_documents}
    Question: {step.sub_question}
    """
    
    response = llm.generate(prompt)
    
    # This should succeed
    assert response == step.expected_inference
```

## Configuration

**File**: `config/narrator_config.yaml`

### Key Settings

```yaml
# LLM parameters
llm:
  temperature: 0.7
  max_tokens: 2000

# Document generation
documents:
  min_count: 15
  max_count: 30
  types: ["email", "network_log", "badge_log", ...]

# Cryptography
cryptography:
  enabled: true
  caesar_probability: 0.3
  vigenere_probability: 0.2
  key_distribution_documents: 3

# Red herrings
red_herrings:
  enabled: true
  count: 3
  types: ["similar_names", "misleading_locations", ...]

# Images
images:
  enabled: true
  count: 5
  model: "black-forest-labs/flux-schnell"
```

## Best Practices

### 1. Start with Demo Mode

Test without API calls:
```bash
python scripts/generate_mystery.py --mode demo
```

### 2. Incremental Difficulty

Start easy, then increase:
```bash
for diff in 3 5 7 9; do
  python scripts/generate_mystery.py --difficulty $diff
done
```

### 3. Validate Before Deploy

Always validate mysteries:
```bash
python scripts/validate_mystery.py <mystery_id>
```

### 4. Monitor Logs

Watch generation progress:
```bash
tail -f outputs/logs/generation_*.log
```

### 5. Check Generated Files

Review outputs before deployment:
```bash
cd outputs/mysteries/mystery_<id>/
cat mystery.json | jq .
ls documents/
```

## Troubleshooting

### Issue: Generation Fails

Check logs for specific error:
```bash
tail -f outputs/logs/generation_*.log
```

### Issue: Documents Don't Contain Clues

Review document planning step:
```python
# Check document plan
with open("narrative_graph.json") as f:
    graph = json.load(f)
    print(graph["document_plans"])
```

### Issue: Validation Fails

Check proof tree structure:
```bash
cat mystery.json | jq '.proof_tree'
```

### Issue: Images Missing Visual Clues

Check VLM validation results:
```bash
cat mystery.json | jq '.images[] | .validation_result'
```

## Next Steps

- [Document Generation](./DOCUMENT_GENERATION.md) - Deep dive into document types
- [Cryptography](./CRYPTOGRAPHY.md) - Cipher system details
- [Validation](./VALIDATION.md) - Validation system guide
- [Configuration](./CONFIGURATION.md) - Config file reference



