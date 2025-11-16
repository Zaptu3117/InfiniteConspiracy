# Environment Variables Guide

## Overview
All scripts properly load `.env` using `dotenv` and require the following variables:

## ✅ Current .env Keys (Verified)
Your `.env` file currently has these keys:
```
ARKIV_PRIVATE_KEY
ARKIV_RPC_URL
CEREBRAS_API_KEY
CONTRACT_ADDRESS
KUSAMA_CHAIN_ID
KUSAMA_RPC_URL
LOG_DIR
LOG_LEVEL
OPENAI_API_KEY
ORACLE_PRIVATE_KEY
REPLICATE_API_TOKEN
```

## Required Variables

### 🧠 LLM API Keys (REQUIRED)
```bash
# Primary LLM for conspiracy generation
CEREBRAS_API_KEY=your_cerebras_api_key_here

# Optional alternative LLM
OPENAI_API_KEY=your_openai_api_key_here

# Image generation (Required)
REPLICATE_API_TOKEN=your_replicate_token_here
```

### ⛓️ Blockchain Configuration (REQUIRED)
```bash
# Deployer wallet (for deploying contracts)
DEPLOYER_PRIVATE_KEY=0x...

# Oracle wallet (for registering mysteries)
ORACLE_PRIVATE_KEY=0x...

# RPC endpoint
KUSAMA_RPC_URL=http://localhost:8545  # or testnet URL

# Chain ID
KUSAMA_CHAIN_ID=31337  # Local hardhat: 31337, Paseo: check docs

# Contract address (auto-populated after deployment)
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
```

### 🗄️ Arkiv Storage (REQUIRED)
```bash
# Arkiv wallet for uploads
ARKIV_PRIVATE_KEY=0x...

# Arkiv RPC endpoint
ARKIV_RPC_URL=http://localhost:8545  # or testnet URL
```

### 📝 Logging (OPTIONAL)
```bash
LOG_DIR=./logs
LOG_LEVEL=INFO
```

## Token Limits (Now Fixed! ✅)

All scripts now use **8000 tokens** for document generation:

- `test_full_e2e_with_contract.py` ✅
- `deploy_conspiracy_to_network.py` ✅
- `test_e2e_conspiracy_arkiv.py` ✅

### Config Structure:
```python
config = {
    "political_context": {"temperature": 0.8, "max_tokens": 8000},
    "conspiracy": {"temperature": 0.8, "max_tokens": 8000},
    "psychological": {"temperature": 0.7, "max_tokens": 8000},
    "cryptographic": {"temperature": 0.7, "max_tokens": 8000},
    "document_generation": {"temperature": 0.7, "max_tokens": 8000, "parallel_batch_size": 5},
    "character_enhancement": {"temperature": 0.7, "max_tokens": 8000},
    "num_images": 2
}
```

## How .env is Loaded

All scripts use this pattern:
```python
from dotenv import load_dotenv
load_dotenv()  # Called at module level

# Then later:
cerebras_key = os.getenv("CEREBRAS_API_KEY")
oracle_key = os.getenv("ORACLE_PRIVATE_KEY")
# etc...
```

## Testing .env Loading

Run this to verify all variables are set:
```bash
cd backend
python -c "
from dotenv import load_dotenv
import os
load_dotenv()

required = [
    'CEREBRAS_API_KEY',
    'ORACLE_PRIVATE_KEY',
    'ARKIV_PRIVATE_KEY',
    'KUSAMA_RPC_URL',
    'ARKIV_RPC_URL'
]

for key in required:
    value = os.getenv(key)
    status = '✅' if value else '❌'
    masked = value[:10] + '...' if value and len(value) > 10 else value
    print(f'{status} {key}: {masked}')
"
```

## Security Notes

⚠️ **NEVER commit .env to git!**
- Already in `.gitignore`
- Already in `.cursorignore`

🔐 **Private Key Format:**
- Must start with `0x`
- Followed by 64 hex characters
- Example: `0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef`

🧪 **For Local Testing (Hardhat):**
Use Hardhat's default test accounts:
```bash
# Account #0 (Deployer)
DEPLOYER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# Account #1 (Oracle)
ORACLE_PRIVATE_KEY=0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
```

## Network-Specific Values

### Local (Hardhat)
```bash
KUSAMA_RPC_URL=http://localhost:8545
KUSAMA_CHAIN_ID=31337
```

### Paseo Testnet
```bash
KUSAMA_RPC_URL=https://paseo-rpc.dwellir.com
KUSAMA_CHAIN_ID=1000  # Verify with testnet docs
```

### Kusama Mainnet
```bash
KUSAMA_RPC_URL=https://kusama-asset-hub-eth-rpc.polkadot.io
KUSAMA_CHAIN_ID=1000
```

## Summary

✅ **Status:**
- `.env` file exists
- All required keys present
- `load_dotenv()` called in all scripts
- Token limits increased to 8000 for all document generation
- Ready for full conspiracy generation!

🚀 **Next Steps:**
1. Test token limits with real conspiracy:
   ```bash
   uv run python test_full_e2e_with_contract.py --contract 0x5FbDB2315678afecb367f032d93F642f64180aa3 --difficulty 5 --docs 10
   ```

2. Deploy to testnet when ready:
   ```bash
   python deploy_contract_to_network.py --network paseo
   python deploy_conspiracy_to_network.py --network paseo --difficulty 5 --docs 10
   ```

