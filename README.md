# Infinite Conspiracy: A Self-Evolving Detective ARG

<p align="center">
  <strong>Blockchain detective game with infinite mysteries, multi-hop reasoning, and automation resistance</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#hackathon">Hackathon</a>
</p>

---

## 🎯 Overview

**Infinite Conspiracy** is a blockchain-based detective game where:

- 🔍 **20+ documents** with scattered clues (cryptography, steganography, cross-references)
- 🧠 **Multi-hop reasoning REQUIRED** - automation-resistant by design
- 💰 **First solver wins bounty** (quadratic staked submissions)
- ⛓️ **No backend API** - pure blockchain + Arkiv architecture
- 🎲 **Infinite mysteries** - generate new cases on-demand

### Key Innovation: Provably Automation-Resistant

Each mystery is **validated** to ensure:
1. ✅ Single LLM call CANNOT solve it (too complex)
2. ✅ Guided multi-hop reasoning CAN solve it (not impossible)
3. ✅ Requires 3-7 reasoning steps minimum
4. ✅ Clues scattered across 20-25 documents

## 🚀 Features

### For Players

- **Inscription System**: One-time 10 KSM fee to prevent sybil attacks
- **Quadratic Submissions**: 1 KSM base + n² penalty (discourages spam)
- **Bounty Accumulation**: All submission fees go to mystery pool
- **On-chain Leaderboard**: Track mysteries solved, bounty won, reputation
- **Proof Revelation**: After expiry, proof tree revealed to show solvability

### For Developers

- **Push-Only Backend**: No API server, just generation + push
- **Arkiv Storage**: Decentralized, queryable, time-scoped documents
- **Smart Contracts**: Full bounty mechanics on Kusama
- **Modular LangGraph**: Easy to customize mystery generation
- **VLM Validation**: Images verified to contain required visual clues

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         BACKEND (Python)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Narrator │→│Documents │→│  Images  │ │
│  │ Pipeline │  │   (JSON) │  │(Replicate)│ │
│  └──────────┘  └──────────┘  └──────────┘ │
│         │                          │        │
│         └──────────┬───────────────┘        │
│                    ↓                        │
│         ┌─────────────────┐                │
│         │  Validation     │                │
│         │  (Anti-Bot)     │                │
│         └─────────────────┘                │
└─────────────────┬──────────────────────────┘
                  ↓
    ┌─────────────┴────────────┐
    │                          │
    ↓                          ↓
┌────────────────┐    ┌──────────────────┐
│ ARKIV MENDOZA  │    │ KUSAMA ASSET HUB │
│  (Data Layer)  │    │  (Blockchain)    │
│                │    │                  │
│ • Documents    │    │ • Smart Contract │
│ • Images       │    │ • Bounties       │
│ • Metadata     │    │ • Submissions    │
│ • 7-day TTL    │    │ • Leaderboard    │
└────────────────┘    └──────────────────┘
    ↑                          ↑
    │                          │
    └──────────┬───────────────┘
               ↓
      ┌────────────────┐
      │   FRONTEND     │
      │   (React)      │
      │                │
      │ Queries Arkiv  │
      │ Calls Kusama   │
      └────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.11+
- LangChain/LangGraph (narrative engine)
- Cerebras API (llama3.1-70b for LLM)
- Replicate API (Flux for images)
- OpenAI GPT-4V (VLM validation)
- Arkiv SDK (storage)
- Web3.py (blockchain)

**Blockchain (Kusama Asset Hub):**
- Solidity 0.8.20
- Hardhat
- OpenZeppelin
- Paseo testnet (Chain ID: 420420422) / Kusama mainnet (Chain ID: 420420418)
- Ethereum-compatible smart contracts on Kusama

**Data Layer (Arkiv Mendoza):**
- Arkiv SDK v1.0.0a5 (primary storage, 7-day TTL)
- Decentralized document/image storage
- JSON configs
- No traditional database

**Note:** Arkiv and Kusama are **two separate networks**:
- **Arkiv**: Data storage only (documents, images, metadata)
- **Kusama**: Smart contracts only (bounties, submissions, leaderboard)

## 📦 Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# uv (fast Python package manager)
# Install from: https://github.com/astral-sh/uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js 18+
node --version

# Git
git --version
```

### Installation

**1. Clone repository:**
```bash
git clone <repo-url>
cd InvestigationBackEnd
```

**2. Setup backend with uv (recommended):**
```bash
# Install dependencies using uv
uv pip install -e .

# Or create a virtual environment first
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Setup environment
cp backend/env.example backend/.env
# Edit .env with your API keys
```

**Alternative: Using pip (slower):**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys
```

**3. Setup contracts:**
```bash
cd ../contracts
npm install
cp .env.example .env
# Edit .env with your keys
```

### Generate Your First Mystery

**1. Deploy contract (optional, use testnet):**
```bash
cd contracts
npx hardhat run scripts/deploy.js --network kusama
# Copy contract address to backend/.env
```

**2. Generate mystery:**
```bash
cd backend
python scripts/generate_mystery.py
```

**3. Push to Arkiv:**
```bash
python scripts/push_to_arkiv.py outputs/mysteries/<mystery_id>
```

**4. Register on blockchain:**
```bash
python scripts/register_on_chain.py outputs/mysteries/<mystery_id>
```

**5. Verify:**
```bash
python scripts/validate_mystery.py outputs/mysteries/<mystery_id>
```

## 📖 Documentation

Comprehensive documentation available in [`docs/`](./docs):

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System design and data flow
- **[ARKIV_INTEGRATION.md](./docs/ARKIV_INTEGRATION.md)** - Data layer usage
- **[SMART_CONTRACT.md](./docs/SMART_CONTRACT.md)** - Contract specifications
- **[FRONTEND_GUIDE.md](./docs/FRONTEND_GUIDE.md)** - Integration guide
- **[API_REFERENCE.md](./docs/API_REFERENCE.md)** - Query examples

## 🎪 Hackathon Submissions

This project is designed for **sub0 2025 Hackathon**:

### Arkiv Main Track ($10k)

**Features:**
- ✅ CRUD: Create entities, query by annotations
- ✅ TTL: 7-day expiry for mystery lifecycle
- ✅ Queries: Complex filters for document retrieval
- ✅ Real-time: Potential for subscription-based mystery drops

**Arkiv Usage:**
- 20-25 document entities per mystery
- 8-12 image entities per mystery
- Metadata entity for mystery info
- Minimal annotations (no spoilers!)
- Efficient TTL management

### Kusama Bounty ($5k)

**Art & Social Experiments:**
- Multi-player detective game
- On-chain reputation system
- Quadratic economics (anti-spam)
- Proof revelation system
- Bounty accumulation mechanics

### Polkadot Main Track ($16k)

**Proof of Concept:**
- Working testnet deployment
- Mystery generation pipeline
- Anti-automation validation
- Integration with partner tech

**Milestone 2 Plan:**
- Cross-chain mystery marketplace
- Player-created mysteries
- NFT rewards for top solvers
- Advanced steganography

## 🔑 Key Files

### Backend
- `backend/src/narrative/langgraph_pipeline.py` - Mystery generation
- `backend/src/arkiv/pusher.py` - Upload to Arkiv
- `backend/src/blockchain/mystery_registration.py` - On-chain registration
- `backend/src/validation/anti_automation.py` - Automation tests

### Contracts
- `contracts/contracts/InfiniteConspiracy.sol` - Main game contract
- `contracts/scripts/deploy.js` - Deployment script
- `contracts/test/InfiniteConspiracy.test.js` - Unit tests

### Scripts
- `backend/scripts/generate_mystery.py` - Generate complete mystery
- `backend/scripts/push_to_arkiv.py` - Upload to Arkiv
- `backend/scripts/register_on_chain.py` - Register on blockchain
- `backend/scripts/reveal_proof.py` - Reveal proof after expiry

## 🛠️ Development

### Running Tests

**Backend tests:**
```bash
cd backend
pytest tests/ -v
```

**Contract tests:**
```bash
cd contracts
npx hardhat test
```

### Linting

```bash
cd backend
pylint src/
black src/

cd contracts
npx hardhat check
```

## 📊 Economics

### Player Costs

| Action | Cost | Destination |
|--------|------|-------------|
| Inscription | 10 KSM | 50% treasury, 50% mystery pools |
| 1st Submission | 1 KSM | Mystery bounty pool |
| 2nd Submission | 2 KSM | Mystery bounty pool |
| 3rd Submission | 5 KSM | Mystery bounty pool |
| 4th Submission | 17 KSM | Mystery bounty pool |

### Bounty Calculation

```
Initial Bounty = 10 KSM (from oracle)
+ (50% × Inscription Fees)
+ (All Submission Fees)
= Total Bounty Pool
```

Winner gets 100% of bounty + reputation boost.

## 🔐 Security

- **Answer Hashes**: SHA256, normalized, no plaintext storage
- **Proof Hashes**: Immutable, revealed after expiry
- **Oracle Role**: Required for mystery creation
- **Reentrancy Protection**: All financial functions protected
- **Quadratic Costs**: Spam prevention
- **Inscription Fee**: Sybil resistance

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](./LICENSE) file

## 🙏 Acknowledgments

- **Arkiv Team** - For decentralized data layer
- **Kusama** - For blockchain infrastructure
- **Polkadot** - For ecosystem support
- **OpenAI** - For GPT-4V validation
- **Replicate** - For image generation
- **Cerebras** - For fast LLM inference

## 📧 Contact

For questions or support:
- Open an issue
- Join our Discord (coming soon)
- Email: [your-email]

---

<p align="center">
  Built with ❤️ for sub0 2025
</p>
