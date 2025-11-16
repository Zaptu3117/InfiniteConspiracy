# Backend Overview

## Introduction

The Infinite Conspiracy backend is a Python-based system that generates detective mystery games using Large Language Models (LLMs), deploys them to decentralized storage (Arkiv), and registers them on blockchain (Kusama).

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Python 3.11+)                   │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ LLM Pipeline     │  │ Conspiracy       │               │
│  │ (narrator_*)     │  │ Pipeline         │               │
│  └────────┬─────────┘  └────────┬─────────┘               │
│           │                     │                           │
│           └──────────┬──────────┘                           │
│                      ↓                                      │
│         ┌────────────────────────┐                         │
│         │  Document Generation   │                         │
│         │  (Parallel Async)      │                         │
│         └────────────┬───────────┘                         │
│                      ↓                                      │
│         ┌────────────────────────┐                         │
│         │  Cryptography System   │                         │
│         │  (Caesar, Vigenère)    │                         │
│         └────────────┬───────────┘                         │
│                      ↓                                      │
│         ┌────────────────────────┐                         │
│         │  Image Generation      │                         │
│         │  (Replicate + VLM)     │                         │
│         └────────────┬───────────┘                         │
│                      ↓                                      │
│         ┌────────────────────────┐                         │
│         │  Validation            │                         │
│         │  (Anti-Automation)     │                         │
│         └────────────┬───────────┘                         │
│                      │                                      │
└──────────────────────┼──────────────────────────────────────┘
                       ↓
       ┌───────────────┴───────────────┐
       │                               │
       ↓                               ↓
┌──────────────┐              ┌─────────────────┐
│    ARKIV     │              │   KUSAMA        │
│ Data Layer   │              │   Blockchain    │
│              │              │                 │
│ - Documents  │              │ - Smart         │
│ - Images     │              │   Contract      │
│ - Metadata   │              │ - Bounties      │
│ - 7-day TTL  │              │ - Leaderboard   │
└──────────────┘              └─────────────────┘
```

## Core Components

### 1. Mystery Generation Pipelines

The backend supports two mystery generation systems:

#### LLM Narrative Pipeline (`src/narrative/pipeline.py`)
- Traditional detective mysteries
- 6-step narrator process
- Character/location/timeline generation
- Document planning and generation
- Proof tree with multi-hop reasoning

#### Conspiracy Pipeline (`src/narrative/conspiracy/conspiracy_pipeline.py`)
- Advanced conspiracy-themed mysteries
- Political context generation
- 4-dimensional answers (WHO, WHAT, WHY, HOW)
- Evidence sub-graphs (identity, psychological, cryptographic)
- Red herring integration

### 2. Document Generation System

**Location**: `src/narrative/document_gen/`

**Features**:
- 12+ document types (emails, logs, reports, diaries, etc.)
- Parallel async generation (10x faster)
- Natural language content with evidence fragments
- Contextual awareness (characters, timeline, locations)

**Document Types**:
- `email` - Email correspondence
- `network_log` - Network activity logs
- `badge_log` - Physical access logs
- `surveillance_log` - Security records
- `police_report` - Official reports
- `diary` - Personal journal entries
- `internal_memo` - Company communications
- `medical_record` - Health records
- `financial_statement` - Financial data
- `newspaper` - News articles
- `technical_manual` - Equipment documentation
- `chat_transcript` - Instant messaging logs

### 3. Cryptography System

**Location**: `src/narrative/crypto_integrator.py`, `src/documents/cryptography.py`

**Cipher Types**:
- **Caesar Cipher**: Shift-based encryption with numeric keys
- **Vigenère Cipher**: Keyword-based encryption

**Key Features**:
- Cross-document key distribution
- Keys hidden in documents or images
- Hints system for key discovery
- Automatic encryption of specific text sections

### 4. Validation System

**Location**: `src/validation/`

**Components**:
- **Anti-Automation Validator**: Ensures LLM can't solve in one call
- **Conspiracy Validator**: Validates conspiracy mystery structure
- **Multi-Hop Testing**: Verifies step-by-step solvability

**Tests**:
1. Single-LLM test (must fail)
2. Multi-hop guided test (must succeed)
3. Answer coverage validation
4. Cryptographic key discoverability

### 5. Arkiv Integration

**Location**: `src/arkiv_integration/`

**Features**:
- Entity creation (documents, images, metadata)
- Batch operations
- Query interface
- TTL management (7-day expiry)
- Strategic annotations (no spoilers)

### 6. Blockchain Integration

**Location**: `src/blockchain/`

**Features**:
- Mystery registration
- Answer hash generation
- Proof hash generation
- Web3 client for Kusama
- Transaction management

### 7. Image Generation

**Location**: `src/images/`

**Features**:
- Replicate API integration (Flux model)
- VLM validation (GPT-4V)
- Visual clue verification
- Batch generation

## Data Flow

### Mystery Generation Flow

```
1. Initialize Parameters
   ↓
2. Generate Political Context (if conspiracy)
   OR Generate Premise (if LLM narrative)
   ↓
3. Generate Characters, Timeline, Locations
   ↓
4. Plan Document Structure
   ↓
5. Generate Documents (Parallel Async)
   ↓
6. Apply Cryptography
   ↓
7. Add Red Herrings
   ↓
8. Generate Images (Optional)
   ↓
9. Validate Mystery
   ↓
10. Generate Hashes
   ↓
11. Save to File System
```

### Deployment Flow

```
1. Load Mystery from File
   ↓
2. Push to Arkiv
   ├─ Create metadata entity
   ├─ Create document entities (batch)
   └─ Create image entities (batch)
   ↓
3. Register on Blockchain
   ├─ Generate answer hash
   ├─ Generate proof hash
   └─ Call createMystery() on contract
   ↓
4. Mystery is Live!
```

## Technology Stack

### Core Technologies
- **Python 3.11+** - Main language
- **asyncio** - Async/await for concurrent operations
- **pydantic** - Data validation and models

### LLM Integration
- **LangChain** - LLM orchestration
- **LangGraph** - Complex workflows (planned)
- **Cerebras API** - Fast LLM inference
- **OpenAI GPT-4V** - Visual validation

### External APIs
- **Arkiv SDK v1.0.0a5** - Decentralized storage
- **Replicate API** - Image generation
- **Web3.py** - Blockchain interaction

### Development Tools
- **uv** - Fast package manager
- **pytest** - Testing framework
- **black** - Code formatting
- **pylint** - Linting

## Project Structure

```
backend/
├── config/
│   └── narrator_config.yaml      # Pipeline configuration
├── scripts/
│   ├── generate_mystery.py       # Main generation script
│   ├── push_to_arkiv.py         # Arkiv deployment
│   ├── register_on_chain.py     # Blockchain registration
│   └── validate_mystery.py      # Validation script
├── src/
│   ├── arkiv_integration/       # Arkiv client and entity builders
│   ├── blockchain/              # Web3 client and contract interaction
│   ├── documents/               # Document generation and crypto
│   ├── images/                  # Image generation and validation
│   ├── models/                  # Data models (Mystery, Document, etc.)
│   ├── narrative/               # Mystery generation pipelines
│   │   ├── conspiracy/          # Conspiracy pipeline
│   │   ├── document_gen/        # Document generators
│   │   ├── graph/               # Narrative graph
│   │   └── narrator/            # Narrator orchestration
│   ├── utils/                   # Utilities (config, logger, clients)
│   └── validation/              # Validation systems
├── tests/                       # Test suite
├── outputs/                     # Generated mysteries
└── docs/                        # This documentation
```

## Key Concepts

### Mystery
A complete detective puzzle with:
- Question to answer
- Documents containing clues
- Images with visual evidence
- Proof tree showing reasoning steps
- Answer and hashes

### Proof Tree
A directed acyclic graph (DAG) of reasoning steps:
- **Leaf nodes**: Direct observations from documents
- **Intermediate nodes**: Inferences from combining evidence
- **Root node**: Final answer

### Multi-Hop Reasoning
Solving requires multiple steps:
1. Read Document A → Extract clue 1
2. Read Document B → Extract clue 2
3. Combine clues 1 + 2 → Inference 1
4. Read Document C → Extract clue 3
5. Combine Inference 1 + clue 3 → Answer

### Anti-Automation
Mysteries are validated to ensure:
- Single LLM call CANNOT solve them
- Guided multi-hop reasoning CAN solve them
- Automation resistance by design

## Configuration

### Environment Variables (`.env`)
```bash
# LLM APIs
CEREBRAS_API_KEY=...
OPENAI_API_KEY=...
REPLICATE_API_TOKEN=...

# Arkiv
ARKIV_RPC_URL=https://mendoza.hoodi.arkiv.network/rpc
ARKIV_PRIVATE_KEY=0x...

# Kusama
KUSAMA_RPC_URL=https://testnet-passet-hub-eth-rpc.polkadot.io
KUSAMA_CHAIN_ID=420420422
ORACLE_PRIVATE_KEY=0x...
CONTRACT_ADDRESS=0x...

# Logging
LOG_LEVEL=INFO
LOG_DIR=outputs/logs
```

### Pipeline Configuration (`config/narrator_config.yaml`)
- LLM parameters (temperature, max_tokens)
- Document counts and types
- Cryptography settings
- Red herring settings
- Image generation settings

## Performance

### Generation Time
- **LLM mysteries**: 2-5 minutes
- **Conspiracy mysteries**: 3-7 minutes
- **Document generation**: 30-60 seconds (parallel)
- **Image generation**: 30-60 seconds per image

### Resource Usage
- **Memory**: ~500MB-1GB
- **Disk**: ~5-10MB per mystery
- **API Costs**: ~$1-2 per mystery

## Scalability

### Current Capabilities
- Single backend instance
- Sequential mystery generation
- Manual deployment

### Future Improvements
- Parallel mystery generation
- Automated deployment pipelines
- Distributed generation workers
- Caching and optimization

## Next Steps

- [Installation Guide](./INSTALLATION.md) - Set up your development environment
- [Quick Start](./QUICK_START.md) - Generate your first mystery
- [Mystery Generation](./MYSTERY_GENERATION.md) - Understand the generation process

