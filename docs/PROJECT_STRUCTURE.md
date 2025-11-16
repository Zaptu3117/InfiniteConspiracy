# Project Structure

Complete file organization and directory structure for Infinite Conspiracy.

## Repository Root

```
InvestigationBackEnd/
├── README.md                    # Project overview, quick start, documentation
├── LICENSE                      # MIT License
├── pyproject.toml              # Python package configuration
├── uv.lock                     # uv package lockfile
│
├── backend/                    # Python backend (mystery generation)
├── contracts/                  # Smart contracts (Solidity)
├── docs/                       # Complete project documentation
└── main.py                     # (legacy - can be removed)
```

## Backend Structure

```
backend/
├── config/
│   └── narrator_config.yaml    # Pipeline configuration
│
├── scripts/                    # Utility and deployment scripts
│   ├── generate_mystery.py     # Main generation script
│   ├── push_to_arkiv.py       # Arkiv deployment
│   ├── register_on_chain.py   # Blockchain registration
│   ├── validate_mystery.py    # Mystery validation
│   ├── deploy_contract_to_network.py    # Deploy contract once
│   ├── deploy_conspiracy_to_network.py  # Deploy conspiracy to network
│   └── deploy_3_conspiracies.py         # Deploy multiple conspiracies
│
├── src/                        # Source code
│   ├── arkiv_integration/     # Arkiv client and entity builders
│   │   ├── __init__.py
│   │   ├── client.py          # Arkiv client wrapper
│   │   ├── entity_builder.py # Entity construction
│   │   └── pusher.py          # Batch upload logic
│   │
│   ├── blockchain/            # Web3 and contract interaction
│   │   ├── __init__.py
│   │   ├── web3_client.py     # Web3 client wrapper
│   │   ├── mystery_registration.py  # Contract calls
│   │   └── proof_manager.py   # Proof revelation
│   │
│   ├── documents/             # Document generation and crypto
│   │   ├── __init__.py
│   │   ├── generator.py       # Document content generation
│   │   └── cryptography.py    # Cipher implementations
│   │
│   ├── images/                # Image generation and validation
│   │   ├── __init__.py
│   │   ├── generator.py       # Replicate API integration
│   │   └── vlm_validator.py   # GPT-4V validation
│   │
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── mystery.py         # Mystery data model
│   │   ├── document.py        # Document data model
│   │   ├── conspiracy.py      # Conspiracy data model
│   │   ├── proof_tree.py      # Proof tree model
│   │   └── validation_result.py  # Validation results
│   │
│   ├── narrative/             # Mystery generation pipelines
│   │   ├── __init__.py
│   │   ├── pipeline.py        # LLM narrative pipeline
│   │   ├── crypto_integrator.py  # Cryptography integration
│   │   ├── red_herrings.py    # Red herring generation
│   │   │
│   │   ├── conspiracy/        # Conspiracy pipeline
│   │   │   ├── __init__.py
│   │   │   ├── conspiracy_pipeline.py  # Main conspiracy pipeline
│   │   │   ├── political_context_generator.py
│   │   │   ├── conspiracy_generator.py
│   │   │   ├── answer_template_generator.py
│   │   │   ├── subgraph_generator.py
│   │   │   ├── subgraph_types.py
│   │   │   ├── document_generator.py
│   │   │   ├── document_name_generator.py
│   │   │   ├── document_subgraph_mapper.py
│   │   │   ├── character_enhancer.py
│   │   │   ├── phrase_encryptor.py
│   │   │   ├── image_clue_mapper.py
│   │   │   ├── red_herring_builder.py
│   │   │   └── nodes/         # Evidence node generators
│   │   │       ├── __init__.py
│   │   │       ├── identity_nodes.py
│   │   │       ├── psychological_nodes.py
│   │   │       └── crypto_nodes.py
│   │   │
│   │   ├── document_gen/      # Document generation
│   │   │   ├── __init__.py
│   │   │   ├── parallel_generator.py  # Parallel async generation
│   │   │   └── document_prompts.py    # LLM prompts
│   │   │
│   │   ├── graph/             # Narrative graph
│   │   │   ├── __init__.py
│   │   │   └── narrative_graph.py
│   │   │
│   │   └── narrator/          # Narrator orchestration
│   │       ├── __init__.py
│   │       ├── narrator_orchestrator.py  # Main orchestrator
│   │       ├── step_minus1_premise.py    # Premise generation
│   │       ├── step0_proof_tree.py       # Proof tree
│   │       ├── step1_characters.py       # Character generation
│   │       ├── step2_timeline.py         # Timeline generation
│   │       ├── step3_locations.py        # Location generation
│   │       ├── step4_document_plan.py    # Document planning
│   │       ├── step5_graph_assembly.py   # Graph assembly
│   │       ├── clue_fragmenter.py        # Clue distribution
│   │       └── identity_injector.py      # Identity injection
│   │
│   ├── utils/                 # Utilities
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration loader
│   │   ├── logger.py          # Logging setup
│   │   └── llm_clients.py     # LLM client wrappers
│   │
│   └── validation/            # Validation systems
│       ├── __init__.py
│       └── conspiracy_validator.py  # Mystery validation
│
├── tests/                     # Complete test suite (all tests organized here)
│   ├── README.md              # Testing documentation
│   ├── run_all_tests.py       # Master test runner
│   │
│   ├── test_setup.py          # Setup validation
│   ├── test_llm_clients.py    # LLM client tests
│   ├── test_arkiv.py          # Arkiv integration tests
│   ├── test_web3.py           # Web3 connection tests
│   ├── test_replicate.py      # Image generation tests
│   │
│   ├── test_conspiracy_foundation.py   # Conspiracy pipeline tests
│   ├── test_conspiracy_full.py         # Full conspiracy generation
│   ├── test_e2e_conspiracy_arkiv.py    # E2E with Arkiv
│   ├── test_full_e2e_with_contract.py  # E2E with contracts
│   ├── test_blockchain_only.py         # Blockchain tests
│   ├── test_multi_hop_validation.py    # Validation tests
│   ├── test_push_conspiracy.py         # Arkiv push tests
│   ├── test_query_arkiv.py             # Arkiv query tests
│   └── ... (other test files)          # Various integration tests
│
├── outputs/                   # Generated mysteries (cleaned regularly)
│   ├── conspiracies/          # Conspiracy mysteries
│   ├── mysteries/             # Mystery output directory (if used)
│   └── logs/                  # Generation logs (cleared regularly)
│
├── contract_addresses.json    # Deployed contract addresses by network
├── env.example                # Environment template
└── requirements.txt           # Python dependencies (deprecated, use pyproject.toml)
```

## Contracts Structure

```
contracts/
├── contracts/                 # Solidity source files
│   └── InfiniteConspiracy.sol # Main game contract
│
├── scripts/                   # Deployment and utility scripts
│   ├── deploy.js              # Main deployment script
│   └── verify.js              # Contract verification
│
├── test/                      # Contract test suite
│   └── InfiniteConspiracy.test.js  # Contract tests
│
├── docs/                      # Contract documentation
│   ├── README.md              # Documentation index
│   ├── CONTRACTS_OVERVIEW.md  # System architecture
│   ├── INSTALLATION.md        # Setup guide
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── CONTRACT_REFERENCE.md  # Complete API reference
│   ├── GAME_MECHANICS.md      # Game mechanics
│   ├── ECONOMICS.md           # Fees and bounties
│   ├── TESTING.md             # Testing guide
│   ├── SECURITY.md            # Security considerations
│   ├── INTEGRATION.md         # Integration guide
│   ├── KUSAMA_ASSET_HUB.md    # Network details
│   └── TESTNET_GUIDE.md       # Testnet usage
│
├── artifacts/                 # Compiled contracts (generated)
├── cache/                     # Hardhat cache (generated)
├── node_modules/              # NPM dependencies (generated)
├── .env.example               # Environment template
├── .env                       # Environment variables (gitignored)
├── hardhat.config.js          # Hardhat configuration
└── package.json               # NPM package configuration
```

## Root Documentation Structure

```
docs/
├── README.md                        # Documentation index
├── ARCHITECTURE.md                  # System design and data flow
├── PROJECT_STRUCTURE.md             # This file
├── ARKIV_INTEGRATION.md             # Data layer integration guide
├── SMART_CONTRACT.md                # Blockchain integration guide
├── FRONTEND_GUIDE.md                # Frontend development guide
├── TESTNET_DEPLOYMENT_GUIDE.md      # Deployment to testnet/mainnet
├── ENV_VARIABLES_GUIDE.md           # Environment variables reference
└── README_DEPLOYMENT.md             # Deployment system overview
```

## Generated Outputs Structure

### Mystery Output

```
outputs/mysteries/mystery_<uuid>/
├── mystery.json               # Complete mystery data
│   ├── metadata               # Mystery metadata
│   ├── answer                 # Correct answer
│   ├── answer_hash            # Keccak256 hash
│   ├── proof_tree             # Reasoning steps
│   ├── proof_hash             # Proof tree hash
│   ├── documents              # Document array
│   ├── images                 # Image array
│   └── validation_details     # Validation results
│
├── documents/                 # Document JSON files
│   ├── doc_1_email.json
│   ├── doc_2_badge_log.json
│   ├── doc_3_network_log.json
│   └── ...
│
└── images/                    # Generated image files
    ├── img_1_badge.png
    ├── img_2_surveillance.png
    └── ...
```

### Conspiracy Output

```
outputs/conspiracies/conspiracy_<uuid>/
├── conspiracy.json            # Complete conspiracy data
│   ├── political_context      # Fictional world
│   ├── premise                # WHO/WHAT/WHY/HOW
│   ├── answer_template        # 4-part answer
│   ├── subgraphs              # Evidence chains
│   ├── documents              # Document array
│   └── images                 # Image array
│
├── documents/                 # Document JSON files
└── images/                    # Generated image files
```

## Configuration Files

### Backend Configuration

**`backend/config/narrator_config.yaml`**:
```yaml
llm:                           # LLM settings
  temperature: 0.7
  max_tokens: 2000

documents:                     # Document generation
  min_count: 15
  max_count: 30
  types: [...]

cryptography:                  # Cipher settings
  enabled: true
  caesar_probability: 0.3
  vigenere_probability: 0.2

red_herrings:                  # Red herring settings
  enabled: true
  count: 3
  types: [...]

images:                        # Image generation
  enabled: true
  count: 5
  model: "black-forest-labs/flux-schnell"
```

**`backend/.env`**:
```bash
# LLM APIs
CEREBRAS_API_KEY=...
OPENAI_API_KEY=...
REPLICATE_API_TOKEN=...

# Arkiv
ARKIV_RPC_URL=...
ARKIV_PRIVATE_KEY=0x...

# Kusama
KUSAMA_RPC_URL=...
KUSAMA_CHAIN_ID=420420422
ORACLE_PRIVATE_KEY=0x...
CONTRACT_ADDRESS=0x...

# Logging
LOG_LEVEL=INFO
LOG_DIR=outputs/logs
```

### Contracts Configuration

**`contracts/.env`**:
```bash
DEPLOYER_PRIVATE_KEY=0x...
ORACLE_PRIVATE_KEY=0x...
KUSAMA_RPC_URL=...
```

**`contracts/hardhat.config.js`**:
```javascript
{
  solidity: "0.8.20",
  networks: {
    kusama: { ... },    // Mainnet
    paseo: { ... }      // Testnet
  }
}
```

## Key Files by Function

### Mystery Generation
- `backend/scripts/generate_mystery.py` - Entry point
- `backend/src/narrative/pipeline.py` - LLM pipeline
- `backend/src/narrative/conspiracy/conspiracy_pipeline.py` - Conspiracy pipeline
- `backend/config/narrator_config.yaml` - Configuration

### Document Generation
- `backend/src/narrative/document_gen/parallel_generator.py` - Parallel generation
- `backend/src/narrative/document_gen/document_prompts.py` - LLM prompts
- `backend/src/documents/generator.py` - Document content

### Cryptography
- `backend/src/narrative/crypto_integrator.py` - Integration logic
- `backend/src/documents/cryptography.py` - Cipher implementations

### Validation
- `backend/src/validation/conspiracy_validator.py` - Main validator
- `backend/scripts/validate_mystery.py` - Validation script

### Arkiv Integration
- `backend/src/arkiv_integration/pusher.py` - Upload logic
- `backend/scripts/push_to_arkiv.py` - Push script

### Blockchain Integration
- `backend/src/blockchain/mystery_registration.py` - Contract calls
- `backend/scripts/register_on_chain.py` - Registration script
- `contracts/contracts/InfiniteConspiracy.sol` - Smart contract

### Testing
- `backend/tests/run_all_tests.py` - Master test runner
- `backend/tests/test_*.py` - Individual test files
- `contracts/test/InfiniteConspiracy.test.js` - Contract tests

## Important Directories

### Source Code
- `backend/src/` - All backend Python code
- `contracts/contracts/` - All Solidity contracts

### Configuration
- `backend/config/` - Backend configuration
- `backend/.env` - Backend environment variables
- `contracts/.env` - Contract environment variables

### Documentation
- `docs/` - All project documentation (consolidated)
- `contracts/docs/` - Contract-specific docs (if present)

### Outputs
- `backend/outputs/mysteries/` - Generated mysteries
- `backend/outputs/conspiracies/` - Generated conspiracies
- `backend/outputs/logs/` - Generation logs

### Tests
- `backend/tests/` - Backend test suite
- `contracts/test/` - Contract test suite

## File Naming Conventions

### Backend Python Files
- `snake_case.py` for all Python files
- `test_*.py` for test files
- `*_generator.py` for generators
- `*_client.py` for API clients

### Contract Files
- `PascalCase.sol` for Solidity contracts
- `camelCase.js` for JavaScript files

### Documentation Files
- `SCREAMING_SNAKE_CASE.md` for all docs
- `README.md` for index files

### Mystery Output Files
- `mystery_<uuid>/` for directories
- `mystery.json` for mystery data
- `doc_<num>_<type>.json` for documents
- `img_<num>_<description>.png` for images

## Size Estimates

### Codebase
- **Backend**: ~10,000 lines Python
- **Contracts**: ~300 lines Solidity
- **Tests**: ~2,000 lines
- **Documentation**: ~20,000 words

### Generated Mysteries
- **Mystery JSON**: ~50-100 KB
- **Documents**: ~5-10 KB each
- **Images**: ~500 KB each
- **Total per mystery**: ~5-10 MB

## Next Steps

- For backend development: See [backend/docs/README.md](../backend/docs/README.md)
- For contract development: See [contracts/docs/README.md](../contracts/docs/README.md)
- For system architecture: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- For integration: See [ARKIV_INTEGRATION.md](./ARKIV_INTEGRATION.md) and [SMART_CONTRACT.md](./SMART_CONTRACT.md)
