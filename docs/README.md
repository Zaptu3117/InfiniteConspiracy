# Infinite Conspiracy Documentation

Complete documentation for the Infinite Conspiracy project - a blockchain-based detective game with infinite mysteries, multi-hop reasoning, and automation resistance.

## 📚 Documentation Structure

### 🚀 Getting Started
- [README.md](../README.md) - Project overview and quick start
- [SETUP.md](../SETUP.md) - Complete installation guide

### 🏗️ Architecture
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design and data flow
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - File organization

### 🔌 Integration Guides
- [ARKIV_INTEGRATION.md](./ARKIV_INTEGRATION.md) - Data layer integration
- [SMART_CONTRACT.md](./SMART_CONTRACT.md) - Blockchain integration
- [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md) - Frontend development guide

### 📖 Component Documentation

#### Backend
See [backend/docs/README.md](../backend/docs/README.md) for complete backend documentation:
- Backend Overview
- Installation Guide
- Quick Start
- Mystery Generation
- Conspiracy System
- Document Generation
- Cryptography
- Validation
- Testing
- API Reference
- Configuration

#### Contracts
See [contracts/docs/README.md](../contracts/docs/README.md) for complete contracts documentation:
- Contracts Overview
- Installation
- Deployment Guide
- Contract Reference
- Game Mechanics
- Economics
- Testing
- Security
- Integration

## 🎯 Quick Navigation

### For Players
- How the game works: [ARCHITECTURE.md](./ARCHITECTURE.md) - "Player Investigation Flow" section
- Game mechanics: [contracts/docs/GAME_MECHANICS.md](../contracts/docs/GAME_MECHANICS.md)
- Economics: [contracts/docs/ECONOMICS.md](../contracts/docs/ECONOMICS.md)

### For Developers
- **Backend Development**: Start with [backend/docs/BACKEND_OVERVIEW.md](../backend/docs/BACKEND_OVERVIEW.md)
- **Contract Development**: Start with [contracts/docs/CONTRACTS_OVERVIEW.md](../contracts/docs/CONTRACTS_OVERVIEW.md)
- **Frontend Development**: Start with [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md)

### For Integrators
- **Arkiv Integration**: [ARKIV_INTEGRATION.md](./ARKIV_INTEGRATION.md)
- **Smart Contract Integration**: [SMART_CONTRACT.md](./SMART_CONTRACT.md)
- **Frontend Integration**: [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md)

## 📂 Project Structure

```
InvestigationBackEnd/
├── README.md                    # Project overview
├── SETUP.md                     # Installation guide
├── LICENSE                      # MIT License
├── pyproject.toml              # Python package config
├── uv.lock                     # Package lockfile
│
├── docs/                       # Root-level documentation
│   ├── README.md              # This file
│   ├── ARCHITECTURE.md        # System architecture
│   ├── PROJECT_STRUCTURE.md   # File organization
│   ├── ARKIV_INTEGRATION.md   # Arkiv usage
│   ├── SMART_CONTRACT.md      # Contract API
│   └── FRONTEND_GUIDE.md      # Frontend guide
│
├── backend/                    # Python backend
│   ├── src/                   # Source code
│   ├── scripts/               # Utility scripts
│   ├── tests/                 # Test suite
│   ├── config/                # Configuration files
│   ├── outputs/               # Generated mysteries
│   └── docs/                  # Backend documentation
│       ├── README.md          # Backend docs index
│       ├── BACKEND_OVERVIEW.md
│       ├── INSTALLATION.md
│       ├── QUICK_START.md
│       └── ... (12+ docs)
│
└── contracts/                  # Smart contracts
    ├── contracts/             # Solidity files
    ├── scripts/               # Deployment scripts
    ├── test/                  # Contract tests
    └── docs/                  # Contract documentation
        ├── README.md          # Contracts docs index
        ├── CONTRACTS_OVERVIEW.md
        ├── INSTALLATION.md
        ├── DEPLOYMENT.md
        └── ... (10+ docs)
```

## 🔑 Key Concepts

### Mystery
A complete detective puzzle with:
- Question to answer (4 parts for conspiracy: WHO/WHAT/WHY/HOW)
- 20-25 documents containing clues
- 5-8 images with visual evidence
- Proof tree showing reasoning steps
- Multi-hop reasoning required

### Dual-Network Architecture
- **Arkiv**: Decentralized data storage (documents, images, metadata)
- **Kusama**: Blockchain (smart contracts, bounties, leaderboard)

### Anti-Automation
Mysteries are validated to ensure:
- ✅ Single LLM call CANNOT solve them (too complex)
- ✅ Guided multi-hop reasoning CAN solve them (not impossible)
- ✅ Requires 3-7 reasoning steps minimum

### Economics
- **Inscription**: 10 KSM (one-time, sybil protection)
- **Submissions**: Quadratic cost (1 + n² KSM)
- **Bounty**: Accumulates from all fees
- **Reputation**: 100 × difficulty per solve

## 🛠️ Technology Stack

### Backend (Python 3.11+)
- LangChain/LangGraph - LLM orchestration
- Arkiv SDK v1.0.0a5 - Data storage
- Cerebras - Fast LLM inference
- OpenAI GPT-4V - Image validation
- Replicate - Image generation
- Web3.py - Blockchain interaction

### Contracts (Solidity 0.8.20)
- Hardhat - Development framework
- OpenZeppelin - Security libraries
- Kusama Asset Hub - EVM-compatible Layer 1

### Data Layer
- Arkiv Mendoza - Decentralized storage with 7-day TTL

### Blockchain
- Kusama Asset Hub - Ethereum-compatible smart contracts

## 📊 Documentation Status

### ✅ Complete & Up-to-Date
- Root documentation (architecture, integration guides)
- Backend documentation (15+ comprehensive guides)
- Contracts documentation (10+ comprehensive guides)
- All code is documented with inline comments

### 🗑️ Removed (Outdated)
- CONSPIRACY_SUMMARY.md
- PROJECT_STATUS.md
- CONSPIRACY_IMPLEMENTATION_STATUS.md
- CONSPIRACY_SYSTEM_PROGRESS.md
- DOCUMENT_TYPE_FIX_SUMMARY.md
- FIXES_SUMMARY.md
- ARCHITECTURE_CLARIFICATION.md
- backend/ASSESSMENT_SUMMARY.md
- backend/README_ASSESSMENT.md
- backend/FIXES_NEEDED.md
- backend/BACKEND_ASSESSMENT_REPORT.md
- backend/MULTI_HOP_VALIDATION_IMPLEMENTED.md

## 🚀 Quick Start Paths

### Generate Your First Mystery
```bash
# 1. Install dependencies
cd backend
uv pip install -e .

# 2. Configure environment
cp env.example .env
# Edit .env with your API keys

# 3. Generate demo mystery
python scripts/generate_mystery.py --mode demo --difficulty 3

# 4. Generate with LLM (requires API keys)
python scripts/generate_mystery.py --mode llm --difficulty 7 --docs 20
```

### Deploy Contracts
```bash
# 1. Install dependencies
cd contracts
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your keys

# 3. Compile
npx hardhat compile

# 4. Test
npx hardhat test

# 5. Deploy to testnet
npx hardhat run scripts/deploy.js --network paseo
```

### Deploy Mystery End-to-End
```bash
# 1. Generate mystery
cd backend
python scripts/generate_mystery.py --mode llm --difficulty 7

# 2. Push to Arkiv
python scripts/push_to_arkiv.py <mystery_id>

# 3. Register on blockchain
python scripts/register_on_chain.py <mystery_id>

# Mystery is now live!
```

## 📖 Learning Path

### Beginner
1. Read [README.md](../README.md) for project overview
2. Follow [SETUP.md](../SETUP.md) to install
3. Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system
4. Try [backend/docs/QUICK_START.md](../backend/docs/QUICK_START.md)

### Intermediate
1. Read [backend/docs/MYSTERY_GENERATION.md](../backend/docs/MYSTERY_GENERATION.md)
2. Understand [ARKIV_INTEGRATION.md](./ARKIV_INTEGRATION.md)
3. Study [SMART_CONTRACT.md](./SMART_CONTRACT.md)
4. Follow [contracts/docs/DEPLOYMENT.md](../contracts/docs/DEPLOYMENT.md)

### Advanced
1. Study [backend/docs/CONSPIRACY_SYSTEM.md](../backend/docs/CONSPIRACY_SYSTEM.md)
2. Read [backend/docs/CRYPTOGRAPHY.md](../backend/docs/CRYPTOGRAPHY.md)
3. Understand [backend/docs/VALIDATION.md](../backend/docs/VALIDATION.md)
4. Review [contracts/docs/SECURITY.md](../contracts/docs/SECURITY.md)

## 🔗 External Resources

### Networks
- **Arkiv Mendoza**: https://mendoza.hoodi.arkiv.network/rpc
- **Kusama Asset Hub (Mainnet)**: https://kusama-asset-hub-eth-rpc.polkadot.io
- **Paseo Testnet**: https://testnet-passet-hub-eth-rpc.polkadot.io

### APIs
- **Cerebras**: https://cerebras.ai/
- **OpenAI**: https://openai.com/
- **Replicate**: https://replicate.com/

### Documentation
- **Arkiv SDK**: https://github.com/arkiv-network/arkiv-sdk
- **Kusama**: https://kusama.network/
- **Polkadot**: https://polkadot.network/

## 💡 Common Questions

### How does the game work?
See [ARCHITECTURE.md](./ARCHITECTURE.md) for complete flow diagrams.

### How do I generate a mystery?
See [backend/docs/QUICK_START.md](../backend/docs/QUICK_START.md).

### How do I deploy contracts?
See [contracts/docs/DEPLOYMENT.md](../contracts/docs/DEPLOYMENT.md).

### How does Arkiv integration work?
See [ARKIV_INTEGRATION.md](./ARKIV_INTEGRATION.md).

### How do smart contracts work?
See [SMART_CONTRACT.md](./SMART_CONTRACT.md).

### How do I integrate with frontend?
See [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md).

### How does validation work?
See [backend/docs/VALIDATION.md](../backend/docs/VALIDATION.md).

### How does cryptography work?
See [backend/docs/CRYPTOGRAPHY.md](../backend/docs/CRYPTOGRAPHY.md).

## 🤝 Contributing

When contributing:
1. Update relevant documentation
2. Add tests for new features
3. Follow existing code style
4. Update this README if adding new docs
5. Run tests before committing

## 📄 License

MIT License - see [LICENSE](../LICENSE) file

## 🙏 Acknowledgments

- **Arkiv Team** - Decentralized data layer
- **Kusama** - Blockchain infrastructure
- **Polkadot** - Ecosystem support
- **OpenAI** - GPT-4V validation
- **Replicate** - Image generation
- **Cerebras** - Fast LLM inference

---

**Built for sub0 2025 Hackathon** 🏆

For questions or support, open an issue on GitHub.



