# Infinite Conspiracy: Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Anti-Automation System](#anti-automation-system)
5. [Security Considerations](#security-considerations)

## System Overview

Infinite Conspiracy is a blockchain-based detective game featuring:

- **Backend (Python)**: Mystery generation using LangGraph
- **Arkiv Data Layer**: Decentralized document storage with TTL
- **Smart Contracts (Solidity)**: Bounty mechanics on Kusama
- **No Traditional API**: Pure push-only architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Python)                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  LangGraph   │  │   Document   │  │    Image     │    │
│  │   Pipeline   │→│  Generation  │→│  Generation  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                                     │            │
│         └─────────────┬───────────────────────┘            │
│                       ↓                                    │
│         ┌─────────────────────────┐                       │
│         │  Anti-Automation        │                       │
│         │  Validation             │                       │
│         └─────────────────────────┘                       │
│                       │                                    │
└───────────────────────┼────────────────────────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        │                               │
        ↓                               ↓
┌──────────────┐              ┌─────────────────┐
│    ARKIV     │              │   SMART         │
│ Data Layer   │              │   CONTRACTS     │
│              │              │   (Kusama)      │
│ - Documents  │              │                 │
│ - Images     │              │ - Bounties      │
│ - Metadata   │              │ - Leaderboard   │
└──────────────┘              └─────────────────┘
        ↑                               ↑
        │                               │
        └───────────────┬───────────────┘
                        ↓
          ┌─────────────────────────┐
          │   FRONTEND (React)      │
          │                         │
          │  - Query Arkiv          │
          │  - Reconstruct UI       │
          │  - Submit answers       │
          └─────────────────────────┘
```

## Core Components

### 1. Narrative Engine (LangGraph)

**Purpose**: Generate mysteries with provable multi-hop reasoning

**Pipeline Nodes**:
1. `InitializeMystery` - Generate premise + answer
2. `SelectDocuments` - Choose document types
3. `GenerateProofTree` - Build reasoning structure
4. `GenerateContent` - Create document JSON
5. `ApplyCryptography` - Distribute cipher keys
6. `InjectRedHerrings` - Add false leads
7. `GenerateImages` - Create visual evidence
8. `ValidateAutomation` - Prove multi-hop required
9. `Finalize` - Package for deployment

**Key Features**:
- Modular design (nodes can be added/removed)
- Config-driven document selection
- Automatic validation of solvability

### 2. Document Generation System

**Format**: Structured JSON (NOT HTML)

Example email document:
```json
{
  "document_id": "doc_5_email",
  "document_type": "email",
  "fields": {
    "from": "john@company.com",
    "to": ["sarah@company.com"],
    "subject": "Meeting Notes",
    "body": "Encrypted text...",
    "timestamp": "2024-11-13T02:30:00Z"
  },
  "cipher_info": {
    "encrypted": true,
    "cipher_type": "caesar",
    "hint": "Check badge logs"
  }
}
```

**Why JSON over HTML?**
- Frontend flexibility (customize rendering)
- Smaller payload size
- Easier parsing and validation
- Cross-platform compatibility

### 3. Cryptography System

**Cipher Types**:
- **Caesar**: Shift value hidden in image (badge number)
- **Substitution**: Alphabet map scattered across 3 documents
- **Vigenère**: Keyword in newspaper headline

**Key Distribution**:
```
Doc 1: Encrypted text
Doc 5: Partial key (1/3)
Doc 12: Partial key (2/3)
Doc 18: Partial key (3/3)
```

**LLM Resistance**:
- Cannot decode without collecting keys
- Requires document cross-referencing
- Some keys in images (OCR needed)

### 4. Arkiv Integration

**Entity Structure**:
```python
{
  "data": json.dumps(document).encode('utf-8'),
  "expiresIn": 604800,  # 7 days
  "stringAnnotations": [
    {"key": "mystery_id", "value": "mystery_001"},
    {"key": "document_type", "value": "email"},
    {"key": "document_id", "value": "doc_5"}
  ],
  "numericAnnotations": [
    {"key": "created_at", "value": 1730000000}
  ]
}
```

**Critical: NO SPOILER ANNOTATIONS**
- ❌ `contains_clue`
- ❌ `hop_level`
- ❌ `cipher_key`
- ✅ Only metadata for querying

### 5. Smart Contract (Kusama)

**Key Functions**:
- `inscribePlayer()` - Pay 10 KSM (50% to treasury, 50% to pools)
- `submitAnswer()` - Quadratic cost (1 + n² KSM)
- `createMystery()` - Oracle registers mystery
- `revealProof()` - Reveal proof after expiry

**Economics**:
- Inscription: 10 KSM split
- Submission: Base 1 KSM + quadratic penalty
- Bounty: Accumulates from submissions
- Reputation: 100 × difficulty per solve

## Data Flow

### Mystery Generation Flow

```
1. LangGraph generates mystery structure
     ↓
2. Proof tree built (3-7 hops)
     ↓
3. Documents generated (20-25 JSON files)
     ↓
4. Images generated + VLM validated
     ↓
5. Cryptography applied (keys scattered)
     ↓
6. Anti-automation validation
     ├─ Single-LLM test (must FAIL)
     └─ Multi-hop test (must SUCCEED)
     ↓
7. Push to Arkiv
     ├─ Documents as entities
     ├─ Images as entities
     └─ Metadata entity
     ↓
8. Register on Smart Contract
     ├─ Answer hash
     ├─ Proof hash
     └─ Initial bounty
     ↓
9. Mystery goes live (7-day TTL)
```

### Player Investigation Flow

```
1. Frontend queries Arkiv
     ↓
2. Receive 20-25 document JSONs
     ↓
3. Reconstruct UI (templates)
     ↓
4. Player investigates
     ├─ Read documents
     ├─ Find cipher keys
     ├─ Decrypt text
     ├─ Cross-reference
     └─ Build reasoning chain
     ↓
5. Submit answer to Smart Contract
     ├─ Pay quadratic cost
     ├─ Contract validates hash
     └─ If correct: bounty transferred
     ↓
6. Winner gets bounty + reputation
```

## Anti-Automation System

### Why It Matters

Without validation, players could:
- Write scripts to brute-force answers
- Use single LLM call to solve instantly
- Automate the entire investigation

### Validation Process

**Test 1: Single-LLM Must Fail**
```python
# Give ALL documents to one LLM call
prompt = f"Documents: {all_docs}\nQuestion: {question}\nAnswer:"
response = llm.generate(prompt)

if response == correct_answer:
    # TOO EASY - regenerate mystery
    return False
```

**Test 2: Multi-Hop Must Succeed**
```python
# Guide LLM step-by-step
for step in proof_tree.steps:
    prompt = f"Docs so far: {discovered_docs}\nQ: {step.sub_question}"
    response = llm.generate(prompt)
    
    if response != step.expected_inference:
        # UNSOLVABLE - regenerate mystery
        return False

# Solvable with guidance!
return True
```

**Success Criteria**:
- ✅ Single LLM fails
- ✅ Multi-hop succeeds
- ✅ 3-7 hops required
- ✅ Each hop uses 2-4 documents

### Proof Tree Structure

```
Layer 1 (Evidence):
  [Doc A] [Doc B] [Doc C] [Doc D]
      ↓       ↓       ↓       ↓
Layer 2 (First Inferences):
  [Person X at Location Y] [Transaction occurred]
            ↓                    ↓
Layer 3 (Second Inferences):
        [Person X made transaction]
                  ↓
Layer 4 (Final Deduction):
          [Person X is guilty]
```

## Security Considerations

### 1. Answer Hash Security

- Answers normalized (lowercase, trimmed)
- SHA256 hashed on-chain
- Backend signs validation
- No plaintext answers stored

### 2. Proof Integrity

- Proof tree hashed before deployment
- Revealed only after mystery solved/expired
- Proves mystery was solvable
- Immutable on-chain

### 3. Submission Economics

- Quadratic cost prevents spam
- First attempt: 1 KSM
- Second: 2 KSM
- Third: 5 KSM
- Fourth: 17 KSM (1 + 16)

### 4. Arkiv Privacy

- Documents public but clues hidden
- No spoiler annotations
- Frontend must reconstruct logic
- TTL ensures auto-cleanup

### 5. Oracle Trust

- Oracle generates mysteries
- Cannot change answer after creation
- Proof hash validates solvability
- Role-based access control

## Performance Considerations

### Generation Time

- Mystery generation: ~2-5 minutes
- Image generation: ~30-60 seconds per image
- VLM validation: ~5-10 seconds per image
- Total: ~5-10 minutes per mystery

### Storage

- Documents: ~5-10 KB each (JSON)
- Images: ~500 KB each
- Total per mystery: ~5-10 MB

### Costs

- Arkiv storage: ~$0.01 per mystery
- LLM generation: ~$0.50 per mystery
- Image generation: ~$0.40 per mystery
- Total: ~$1 per mystery

## Scalability

### Current Limits

- 1 mystery generated at a time
- Manual oracle operation
- Single backend instance

### Future Improvements

- Parallel mystery generation
- Automated mystery lifecycle
- Multiple oracle operators
- Distributed generation

---

**Next**: See [ARKIV_INTEGRATION.md](./ARKIV_INTEGRATION.md) for data layer details.

