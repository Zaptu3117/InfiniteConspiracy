# Setup Guide

Complete installation and setup instructions for Infinite Conspiracy.

## Prerequisites

### Required Software

```bash
# Python 3.11 or higher
python3 --version  # Should be 3.11+

# uv (fast Python package manager)
# Install from: https://github.com/astral-sh/uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js 18 or higher
node --version     # Should be 18+
npm --version

# Git
git --version
```

### API Keys Required

You will need accounts and API keys from:

1. **Cerebras** (https://cerebras.ai/) - For LLM generation
2. **OpenAI** (https://openai.com/) - For GPT-4V validation
3. **Replicate** (https://replicate.com/) - For image generation
4. **Arkiv** - Ethereum private key for data layer
5. **Kusama/Polkadot** - Private keys for blockchain interaction

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd InvestigationBackEnd
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies using uv (recommended)
uv pip install -e .

# Or use traditional pip
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Backend Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

Required `.env` variables:

```bash
# LLM APIs
CEREBRAS_API_KEY=your_cerebras_key_here
OPENAI_API_KEY=your_openai_key_here

# Image Generation
REPLICATE_API_TOKEN=your_replicate_token_here

# Arkiv Data Layer (Mendoza Testnet)
ARKIV_RPC_URL=https://mendoza.hoodi.arkiv.network/rpc
ARKIV_PRIVATE_KEY=0x...  # Your Ethereum private key for Arkiv

# Kusama Blockchain (Paseo Testnet - use testnet for development)
KUSAMA_RPC_URL=https://testnet-passet-hub-eth-rpc.polkadot.io
KUSAMA_CHAIN_ID=420420422
ORACLE_PRIVATE_KEY=0x...  # Your oracle private key
CONTRACT_ADDRESS=0x...    # Filled after deployment

# Logging
LOG_LEVEL=INFO
LOG_DIR=outputs/logs
```

### 4. Test Backend Setup

```bash
# Run all integration tests
python tests/run_all_tests.py

# Or run individual tests
python tests/test_llm_clients.py
python tests/test_arkiv.py
python tests/test_web3.py
python tests/test_replicate.py  # Uses API credits
```

If you see errors, check:
- Dependencies are installed: `uv pip install -e .`
- All API keys are set in `.env`
- Python version is 3.11+

### 5. Contracts Setup

```bash
cd ../contracts

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env
nano .env
```

Required contracts `.env` variables:

```bash
# Deployer account (needs testnet KSM)
DEPLOYER_PRIVATE_KEY=0x...

# Oracle account (can be same as deployer for testing)
ORACLE_PRIVATE_KEY=0x...

# Network RPC (Kusama Asset Hub with Ethereum compatibility)
# Testnet (recommended):
KUSAMA_RPC_URL=https://testnet-passet-hub-eth-rpc.polkadot.io
# Mainnet:
# KUSAMA_RPC_URL=https://kusama-asset-hub-eth-rpc.polkadot.io
```

### 6. Compile Contracts

```bash
# Compile contracts
npx hardhat compile

# Expected output:
# Compiled 1 Solidity file successfully
```

### 7. Run Contract Tests

```bash
# Run tests
npx hardhat test

# Expected output:
# ✓ Should set the correct oracle role
# ✓ Should allow player inscription
# ... (more tests)
```

## Deployment

### 1. Get Testnet Funds

For **Kusama testnet (Paseo)**:

1. Generate a test account or use existing
2. Get testnet tokens from faucet
3. Export private key (0x format)
4. Add to contracts/.env as `DEPLOYER_PRIVATE_KEY`

### 2. Deploy Smart Contract

```bash
cd contracts

# Deploy to Kusama testnet
npx hardhat run scripts/deploy.js --network kusama

# Output will show:
# 🚀 Deploying InfiniteConspiracy contract...
# ✅ Contract deployed to: 0x...
# 💾 Deployment info saved to deployment.json
```

Copy the contract address and add to `backend/.env`:

```bash
CONTRACT_ADDRESS=0x<deployed_address>
```

### 3. Verify Deployment

```bash
# Check deployment info
cat deployment.json

# Should show:
# {
#   "network": "kusama",
#   "contract": "0x...",
#   "deployer": "0x...",
#   "oracle": "0x...",
#   ...
# }
```

## First Mystery Generation

### Demo Mode (No API Calls)

For testing without API keys:

```bash
cd backend

# Generate demo mystery (uses hardcoded content)
python scripts/generate_mystery.py --mode demo --difficulty 5 --docs 20

# Output will show:
# ✅ Mystery generation complete!
# Mystery ID: <uuid>
# Output: outputs/mysteries/<uuid>
```

### LLM Mode (Full Pipeline)

With all API keys configured:

```bash
cd backend

# 1. Generate mystery with LLM (includes premise, narrator, documents)
python scripts/generate_mystery.py --mode llm --difficulty 7 --docs 23

# 2. Push to Arkiv
python scripts/push_to_arkiv.py <mystery_id>

# 3. Register on blockchain
python scripts/register_on_chain.py <mystery_id>

# Mystery is now live!
```

## Verification

### Backend Verification

```bash
cd backend
python tests/run_all_tests.py

# Should show:
# ✅ Passed: X/X (100%)
# 🎉 ALL TESTS PASSED!
```

### Contracts Verification

```bash
cd contracts
npx hardhat test

# Should show:
# ✅ All tests passing
```

### Integration Verification

```bash
# Generate and push a test mystery
cd backend
python scripts/generate_mystery.py --mode demo --difficulty 3
python scripts/push_to_arkiv.py <mystery_id>
python scripts/register_on_chain.py <mystery_id>

# Mystery is now queryable on Arkiv and registered on Kusama!
```

## Troubleshooting

### Backend Issues

**Issue:** `ModuleNotFoundError: No module named 'dotenv'`

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Issue:** `Configuration validation failed`

**Solution:**
- Check `.env` file exists
- Verify all required API keys are set
- Ensure no quotes around values

**Issue:** `Arkiv connection failed`

**Solution:**
- Verify `ARKIV_PRIVATE_KEY` is valid
- Check network connectivity
- Try Arkiv testnet URLs

### Contract Issues

**Issue:** `Error: insufficient funds`

**Solution:**
- Get testnet tokens from faucet
- Verify deployer account has balance

**Issue:** `Error: contract already deployed`

**Solution:**
- Use different deployer account
- Or deploy to different network

**Issue:** `HardhatError: HH108: Cannot connect to network`

**Solution:**
- Check RPC URL is correct
- Verify network is accessible
- Try alternative RPC endpoints

### Mystery Generation Issues

**Issue:** `API rate limit exceeded`

**Solution:**
- Wait a few minutes
- Use demo mode (`--no-api` flag if available)
- Check API quota limits

**Issue:** `Validation failed: Single LLM solved it`

**Solution:**
- Increase mystery difficulty
- Add more documents
- Scatter clues more widely

**Issue:** `Validation failed: Multi-hop unsolvable`

**Solution:**
- Verify proof tree is correct
- Check documents contain required clues
- Review LangGraph configuration

## Development Workflow

### Typical Development Cycle

```bash
# 1. Make changes to code
nano backend/src/...

# 2. Test changes
cd backend
python tests/run_all_tests.py

# 3. Generate test mystery
python scripts/generate_mystery.py --mode demo --difficulty 5

# 4. If contract changes, recompile and test
cd ../contracts
npx hardhat compile
npx hardhat test

# 5. Redeploy if needed
npx hardhat run scripts/deploy.js --network paseo

# 6. Update backend .env with new contract address
```

### Running Tests

```bash
# Backend integration tests
cd backend
python tests/run_all_tests.py

# Or run individually
python tests/test_llm_clients.py
python tests/test_arkiv.py
python tests/test_web3.py

# Contract tests
cd ../contracts
npx hardhat test
```

### Viewing Logs

```bash
# Backend logs
tail -f backend/outputs/logs/generation_*.log

# Contract deployment logs
cat contracts/deployment.json
```

## Next Steps

After successful setup:

1. **Read Documentation:**
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
   - [ARKIV_INTEGRATION.md](docs/ARKIV_INTEGRATION.md) - Data layer usage
   - [SMART_CONTRACT.md](docs/SMART_CONTRACT.md) - Contract API

2. **Generate Mysteries:**
   - Start with demo mode
   - Test with API keys
   - Deploy to production

3. **Build Frontend:**
   - See [FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md)
   - Create React app
   - Integrate with Arkiv + Contract

4. **Deploy:**
   - Deploy contract to mainnet
   - Set up automation
   - Monitor system

## Support

For issues or questions:

1. Check documentation in `docs/`
2. Review troubleshooting section
3. Open GitHub issue
4. Contact team

## Security Notes

⚠️ **Important Security Reminders:**

- **Never commit `.env` files** to version control
- **Never share private keys** publicly
- **Use testnet** for development
- **Test thoroughly** before mainnet deployment
- **Keep dependencies updated** for security patches

---

**You're all set! Start generating mysteries! 🎉**

