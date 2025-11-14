# Project Structure

Complete directory and file layout for Infinite Conspiracy.

## Root Structure

```
InvestigationBackEnd/
├── backend/              # Python backend for mystery generation
├── contracts/            # Solidity smart contracts
├── docs/                 # Documentation
├── .gitignore
├── LICENSE
└── README.md
```

## Backend Structure

```
backend/
├── config/                          # Configuration files
│   ├── cipher_configs.json          # Cipher types and settings
│   ├── document_types.json          # Document template configs
│   └── langgraph_config.yaml        # LangGraph pipeline settings
│
├── scripts/                         # Executable scripts
│   ├── generate_mystery.py          # Generate complete mystery
│   ├── push_to_arkiv.py            # Upload to Arkiv
│   ├── register_on_chain.py        # Register on blockchain
│   └── reveal_proof.py             # Reveal proof after expiry
│
├── src/                            # Source code
│   ├── arkiv/                      # Arkiv integration
│   │   ├── __init__.py
│   │   ├── client.py               # Arkiv SDK wrapper
│   │   ├── entity_builder.py      # Build Arkiv entities
│   │   └── pusher.py               # Push to Arkiv
│   │
│   ├── blockchain/                 # Blockchain integration
│   │   ├── __init__.py
│   │   ├── web3_client.py          # Web3.py wrapper
│   │   ├── mystery_registration.py # Register mysteries
│   │   └── proof_manager.py        # Proof revelation
│   │
│   ├── documents/                  # Document generation
│   │   ├── __init__.py
│   │   ├── generator.py            # Document generator
│   │   ├── cryptography.py         # Cipher management
│   │   ├── cross_reference.py      # Cross-reference chains
│   │   └── templates/              # Jinja2 templates
│   │       ├── email.json.j2
│   │       ├── diary.json.j2
│   │       ├── police_report.json.j2
│   │       └── ... (more templates)
│   │
│   ├── images/                     # Image generation
│   │   ├── __init__.py
│   │   ├── generator.py            # Replicate API integration
│   │   └── vlm_validator.py        # GPT-4V validation
│   │
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   ├── mystery.py              # Mystery model
│   │   ├── document.py             # Document model
│   │   ├── proof_tree.py           # Proof tree model
│   │   └── validation_result.py    # Validation result model
│   │
│   ├── narrative/                  # LangGraph pipeline
│   │   ├── __init__.py
│   │   ├── langgraph_pipeline.py   # Complete pipeline
│   │   ├── nodes/                  # Pipeline nodes
│   │   │   ├── __init__.py
│   │   │   ├── initialize.py
│   │   │   ├── select_documents.py
│   │   │   ├── generate_proof_tree.py
│   │   │   ├── generate_content.py
│   │   │   ├── apply_crypto.py
│   │   │   ├── inject_red_herrings.py
│   │   │   ├── generate_images.py
│   │   │   ├── validate.py
│   │   │   └── finalize.py
│   │   └── state.py                # Pipeline state
│   │
│   ├── utils/                      # Utilities
│   │   ├── __init__.py
│   │   ├── config.py               # Config management
│   │   ├── logger.py               # Logging setup
│   │   └── llm_clients.py          # LLM API wrappers
│   │
│   └── validation/                 # Anti-automation
│       ├── __init__.py
│       └── anti_automation.py      # Validation logic
│
├── tests/                          # Unit tests
│   ├── test_models.py
│   ├── test_arkiv.py
│   ├── test_documents.py
│   └── test_validation.py
│
├── outputs/                        # Generated outputs
│   ├── mysteries/                  # Mystery directories
│   │   └── <mystery_id>/
│   │       ├── mystery.json
│   │       ├── proof_tree.json
│   │       ├── documents/
│   │       └── images/
│   └── logs/                       # Log files
│
├── env.example                     # Environment template
├── requirements.txt                # Python dependencies
└── test_setup.py                  # Setup verification
```

## Contracts Structure

```
contracts/
├── contracts/                      # Solidity contracts
│   └── InfiniteConspiracy.sol     # Main game contract
│
├── scripts/                        # Deployment scripts
│   ├── deploy.js                   # Deploy contract
│   └── verify.js                   # Verify on explorer
│
├── test/                          # Contract tests
│   └── InfiniteConspiracy.test.js # Unit tests
│
├── artifacts/                     # Compiled contracts
├── cache/                         # Build cache
│
├── hardhat.config.js              # Hardhat configuration
├── package.json                   # Node dependencies
└── deployment.json                # Deployment info
```

## Documentation Structure

```
docs/
├── ARCHITECTURE.md                # System architecture
├── ARKIV_INTEGRATION.md           # Arkiv usage guide
├── SMART_CONTRACT.md              # Contract documentation
├── FRONTEND_GUIDE.md              # Frontend integration
├── PROJECT_STRUCTURE.md           # This file
└── API_REFERENCE.md               # API reference (future)
```

## Key File Purposes

### Backend Files

**Configuration:**
- `config/document_types.json` - Defines all document types, templates, and weights
- `config/cipher_configs.json` - Cipher types and encryption settings
- `config/langgraph_config.yaml` - Pipeline configuration and generation parameters

**Scripts:**
- `scripts/generate_mystery.py` - Main entry point for mystery generation
- `scripts/push_to_arkiv.py` - Upload generated mystery to Arkiv
- `scripts/register_on_chain.py` - Register mystery on smart contract
- `scripts/reveal_proof.py` - Reveal proof after mystery expires

**Core Modules:**
- `src/models/` - Pydantic data models for type safety
- `src/utils/` - Configuration, logging, LLM clients
- `src/arkiv/` - Arkiv SDK integration and entity building
- `src/blockchain/` - Web3 integration and contract interaction
- `src/documents/` - Document generation, encryption, cross-references
- `src/images/` - Image generation and VLM validation
- `src/validation/` - Anti-automation testing
- `src/narrative/` - LangGraph pipeline (modular mystery generation)

### Contract Files

**Smart Contracts:**
- `contracts/InfiniteConspiracy.sol` - Main game logic
  - Player inscription
  - Mystery registration
  - Answer submission with quadratic costs
  - Bounty distribution
  - Leaderboard
  - Proof revelation

**Scripts:**
- `scripts/deploy.js` - Deploy contract to Kusama testnet
- `scripts/verify.js` - Verify contract on block explorer

**Tests:**
- `test/InfiniteConspiracy.test.js` - Contract unit tests

### Documentation Files

- `ARCHITECTURE.md` - Overall system design and data flow
- `ARKIV_INTEGRATION.md` - How to use Arkiv for storage
- `SMART_CONTRACT.md` - Contract API and economics
- `FRONTEND_GUIDE.md` - React integration examples
- `PROJECT_STRUCTURE.md` - This file

## File Naming Conventions

### Python Files

- **Modules:** `lowercase_with_underscores.py`
- **Classes:** `PascalCase` (e.g., `ArkivClient`, `MysteryGenerator`)
- **Functions:** `snake_case` (e.g., `generate_mystery`, `push_to_arkiv`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_DOCUMENTS`, `DEFAULT_TTL`)

### Solidity Files

- **Contracts:** `PascalCase.sol` (e.g., `InfiniteConspiracy.sol`)
- **Functions:** `camelCase` (e.g., `inscribePlayer`, `submitAnswer`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `INSCRIPTION_FEE`)

### JavaScript Files

- **Scripts:** `kebab-case.js` (e.g., `deploy.js`)
- **Functions:** `camelCase`
- **Constants:** `UPPER_SNAKE_CASE`

### JSON/YAML Files

- **Config:** `snake_case.json` or `kebab-case.yaml`

## Important Paths

### Backend

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "documents" / "templates"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = OUTPUTS_DIR / "logs"
```

### Contracts

```javascript
const CONTRACTS_DIR = path.join(__dirname, "..", "contracts");
const ARTIFACTS_DIR = path.join(__dirname, "..", "artifacts");
const DEPLOYMENT_FILE = path.join(__dirname, "..", "deployment.json");
```

## Environment Variables

Required environment variables (copy from `env.example` to `.env`):

```bash
# Backend
CEREBRAS_API_KEY=...
OPENAI_API_KEY=...
REPLICATE_API_TOKEN=...
ARKIV_PRIVATE_KEY=...
ARKIV_RPC_URL=...
ORACLE_PRIVATE_KEY=...
CONTRACT_ADDRESS=...

# Contracts
DEPLOYER_PRIVATE_KEY=...
KUSAMA_RPC_URL=...
```

## Generated Outputs

### Mystery Directory

Each mystery generates:

```
outputs/mysteries/<mystery_id>/
├── mystery.json              # Complete mystery data
├── proof_tree.json           # Proof tree structure
├── documents/                # Individual document JSONs
│   ├── doc_1_email.json
│   ├── doc_2_badge_log.json
│   └── ...
└── images/                   # Generated images
    ├── img_1_badge.png
    ├── img_2_surveillance.png
    └── ...
```

### Mystery JSON Structure

```json
{
  "metadata": {
    "mystery_id": "uuid-here",
    "question": "Who leaked the documents?",
    "difficulty": 7,
    "total_documents": 23,
    "total_images": 8,
    "created_at": 1730000000,
    "expires_in": 604800
  },
  "answer": "Sarah Martinez",
  "answer_hash": "0x...",
  "proof_hash": "0x...",
  "proof_tree": { /* inference nodes and validation steps */ },
  "documents": [ /* document objects */ ],
  "images": [ /* image metadata */ ],
  "validation_passed": true,
  "validation_details": { /* validation results */ }
}
```

## Development Workflow

### 1. Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with API keys

# Contracts
cd contracts
npm install
cp .env.example .env
# Edit .env with keys
```

### 2. Development

```bash
# Test backend setup
python backend/test_setup.py

# Generate mystery (demo mode, no API calls)
python backend/scripts/generate_mystery.py

# Deploy contract
cd contracts
npx hardhat run scripts/deploy.js --network kusama

# Full workflow (requires API keys)
python backend/scripts/generate_mystery.py --difficulty 7
python backend/scripts/push_to_arkiv.py <mystery_id>
python backend/scripts/register_on_chain.py <mystery_id> --bounty 10.0
```

### 3. Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Contract tests
cd contracts
npx hardhat test
```

## Dependencies

### Python (backend/requirements.txt)

```
langchain>=0.1.0
langgraph>=0.0.20
arkiv-sdk>=0.1.19
replicate>=0.15.0
openai>=1.10.0
web3>=6.15.0
jinja2>=3.1.2
python-dotenv>=1.0.0
pydantic>=2.5.0
pytest>=7.4.0
pyyaml>=6.0.1
aiofiles>=23.2.1
```

### Node (contracts/package.json)

```json
{
  "@nomicfoundation/hardhat-toolbox": "^4.0.0",
  "@openzeppelin/contracts": "^5.0.0",
  "hardhat": "^2.19.0",
  "dotenv": "^16.3.1"
}
```

## Git Ignore Patterns

See `.gitignore` for complete list. Key exclusions:
- `__pycache__/`, `*.pyc`
- `venv/`, `env/`
- `node_modules/`
- `.env`, `backend/.env`, `contracts/.env`
- `outputs/`
- `contracts/artifacts/`, `contracts/cache/`
- `.vscode/`, `.idea/`

---

**Next**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design details.

