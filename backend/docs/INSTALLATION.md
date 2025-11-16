# Installation Guide

Complete setup instructions for the Infinite Conspiracy backend.

## Prerequisites

### Required Software

#### Python 3.11+
```bash
python3 --version  # Should be 3.11 or higher
```

If you need to install Python 3.11+:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS (using Homebrew)
brew install python@3.11

# Windows
# Download from https://www.python.org/downloads/
```

#### uv (Fast Python Package Manager)
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Required API Keys

You will need accounts and API keys from:

| Service | Purpose | Sign Up |
|---------|---------|---------|
| **Cerebras** | LLM generation | https://cerebras.ai/ |
| **OpenAI** | GPT-4V validation | https://openai.com/ |
| **Replicate** | Image generation | https://replicate.com/ |
| **Arkiv** | Ethereum private key | Generate with Web3 wallet |
| **Kusama** | Blockchain interaction | Generate with Polkadot wallet |

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd InvestigationBackEnd/backend
```

### 2. Install Dependencies

#### Option A: Using uv (Recommended)

```bash
# Install from project root
cd /path/to/InvestigationBackEnd
uv pip install -e .

# Or create a virtual environment first
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Option B: Using pip

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Verify Installation

```bash
python -c "import arkiv_sdk; import web3; import langchain; print('✅ All packages installed')"
```

### 3. Configure Environment

```bash
cd backend
cp env.example .env
```

Edit `.env` with your API keys:

```bash
# LLM APIs
CEREBRAS_API_KEY=your_cerebras_key_here
OPENAI_API_KEY=sk-...

# Image Generation
REPLICATE_API_TOKEN=r8_...

# Arkiv Data Layer (Mendoza Testnet)
ARKIV_RPC_URL=https://mendoza.hoodi.arkiv.network/rpc
ARKIV_PRIVATE_KEY=0x...  # Your Ethereum private key

# Kusama Blockchain (Testnet)
KUSAMA_RPC_URL=https://testnet-passet-hub-eth-rpc.polkadot.io
KUSAMA_CHAIN_ID=420420422
ORACLE_PRIVATE_KEY=0x...  # Your oracle private key
CONTRACT_ADDRESS=0x...    # Will be filled after contract deployment

# Logging
LOG_LEVEL=INFO
LOG_DIR=outputs/logs
```

### 4. Verify Setup

```bash
# Run basic tests
python -m pytest tests/test_setup.py -v

# Expected output:
# ✅ Config loads successfully
# ✅ LLM clients initialize
# ✅ Arkiv client connects
# ✅ Web3 client connects
```

## Configuration Details

### Cerebras API Key

1. Sign up at https://cerebras.ai/
2. Navigate to API Keys section
3. Create new API key
4. Copy to `.env` as `CEREBRAS_API_KEY`

**Models used**: `llama3.1-70b` (fast inference)

### OpenAI API Key

1. Sign up at https://platform.openai.com/
2. Go to API Keys
3. Create new secret key
4. Copy to `.env` as `OPENAI_API_KEY`

**Models used**: `gpt-4-vision-preview` (image validation)

### Replicate API Token

1. Sign up at https://replicate.com/
2. Go to Account Settings → API Tokens
3. Copy your default token
4. Add to `.env` as `REPLICATE_API_TOKEN`

**Models used**: `black-forest-labs/flux-schnell` (image generation)

### Arkiv Private Key

Generate an Ethereum private key for Arkiv:

```bash
# Using Python
python3 -c "from web3 import Web3; w3 = Web3(); acc = w3.eth.account.create(); print(f'Address: {acc.address}\\nPrivate Key: {acc.key.hex()}')"
```

**Important**: This is for testnet only. Never use testnet keys on mainnet!

### Kusama Private Keys

Generate keys for Kusama Asset Hub:

```bash
# Using Python
python3 -c "from web3 import Web3; w3 = Web3(); acc = w3.eth.account.create(); print(f'Address: {acc.address}\\nPrivate Key: {acc.key.hex()}')"
```

You need two keys:
- `ORACLE_PRIVATE_KEY` - For creating mysteries
- Optionally the same key can be used for both oracle and deployer

#### Get Testnet Tokens

For **Paseo testnet** (Kusama testnet):
1. Use the address generated above
2. Request testnet tokens from faucet (check Polkadot Discord)
3. Wait for confirmation

## Testing Installation

### Run All Tests

```bash
cd backend
python tests/run_all_tests.py
```

Expected output:
```
============================================================
🧪 RUNNING INTEGRATED TEST SUITE
============================================================

Test 1: LLM Clients (Cerebras + OpenAI)
============================================================
✅ LLM test passed

Test 2: Arkiv SDK Integration
============================================================
✅ Arkiv test passed

Test 3: Web3 Blockchain Connection
============================================================
✅ Web3 test passed

Test 4: Replicate Image Generation
============================================================
✅ Replicate test passed

============================================================
✅ Passed: 4/4 (100%)
🎉 ALL TESTS PASSED!
============================================================
```

### Run Individual Tests

```bash
# Test LLM clients
python tests/test_llm_clients.py

# Test Arkiv connection
python tests/test_arkiv.py

# Test blockchain connection
python tests/test_web3.py

# Test image generation (uses API credits!)
python tests/test_replicate.py
```

## Troubleshooting

### Issue: `ModuleNotFoundError`

**Error**: `ModuleNotFoundError: No module named 'arkiv_sdk'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or .venv/bin/activate

# Reinstall dependencies
uv pip install -e .
# or
pip install -r requirements.txt
```

### Issue: `Configuration validation failed`

**Error**: Configuration errors on startup

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify all required keys are set
cat .env | grep -v '^#' | grep '='

# Ensure no quotes around values
# Wrong: CEREBRAS_API_KEY="abc123"
# Right: CEREBRAS_API_KEY=abc123
```

### Issue: `Arkiv connection failed`

**Error**: Cannot connect to Arkiv network

**Solution**:
```bash
# Verify private key format (should start with 0x)
echo $ARKIV_PRIVATE_KEY

# Test RPC connection
curl https://mendoza.hoodi.arkiv.network/rpc \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Should return: {"jsonrpc":"2.0","id":1,"result":"0x..."}
```

### Issue: `Web3 connection failed`

**Error**: Cannot connect to Kusama

**Solution**:
```bash
# Test RPC endpoint
curl https://testnet-passet-hub-eth-rpc.polkadot.io \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'

# Should return: {"jsonrpc":"2.0","id":1,"result":"0x19105746"} (420420422 in hex)

# Verify private key format
python3 -c "from web3 import Web3; print(Web3().eth.account.from_key('YOUR_PRIVATE_KEY').address)"
```

### Issue: `Cerebras API error`

**Error**: 401 Unauthorized or rate limit

**Solution**:
```bash
# Test API key
curl https://api.cerebras.ai/v1/models \
  -H "Authorization: Bearer $CEREBRAS_API_KEY"

# Check rate limits in Cerebras dashboard
# Wait if rate limited, or upgrade plan
```

### Issue: `OpenAI API error`

**Error**: Insufficient quota or invalid key

**Solution**:
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check billing: https://platform.openai.com/account/billing
# Add payment method if needed
```

### Issue: `Replicate API error`

**Error**: Authentication failed or model not found

**Solution**:
```bash
# Test API token
curl https://api.replicate.com/v1/models \
  -H "Authorization: Token $REPLICATE_API_TOKEN"

# Check credits: https://replicate.com/account/billing
```

## Platform-Specific Notes

### Windows (WSL2)

If using WSL2, ensure you're inside WSL:

```bash
# Check if in WSL
uname -r  # Should show "microsoft"

# Install in WSL, not Windows
cd /home/<username>/projects/InvestigationBackEnd
```

### macOS (Apple Silicon)

Some packages may need Rosetta or ARM-specific builds:

```bash
# If you encounter issues, try:
arch -arm64 brew install python@3.11
arch -arm64 pip install -r requirements.txt
```

### Linux

Ensure development headers are installed:

```bash
# Ubuntu/Debian
sudo apt install python3.11-dev libssl-dev build-essential

# Fedora/RHEL
sudo dnf install python3.11-devel openssl-devel gcc
```

## Next Steps

After successful installation:

1. **Generate a test mystery**:
   ```bash
   python scripts/generate_mystery.py --mode demo --difficulty 3
   ```

2. **Read the Quick Start guide**: [QUICK_START.md](./QUICK_START.md)

3. **Understand the generation pipeline**: [MYSTERY_GENERATION.md](./MYSTERY_GENERATION.md)

4. **Deploy contract and test end-to-end**: See contracts documentation

## Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review test output: `python tests/run_all_tests.py`
3. Check logs: `tail -f outputs/logs/generation_*.log`
4. Open an issue on GitHub with error details


