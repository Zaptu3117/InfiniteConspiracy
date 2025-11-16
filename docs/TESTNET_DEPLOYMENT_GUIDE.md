# 🌐 Testnet Deployment Guide

Complete guide for deploying InfiniteConspiracy to Paseo (testnet) and Kusama (mainnet).

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Testing](#local-testing)
3. [Paseo Testnet Deployment](#paseo-testnet-deployment)
4. [Kusama Mainnet Deployment](#kusama-mainnet-deployment)
5. [Contract Address Management](#contract-address-management)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### 1. Environment Setup

Create a `.env` file in `backend/` with:

```bash
# LLM API Keys
CEREBRAS_API_KEY=your_cerebras_key

# Image Generation (optional)
REPLICATE_API_TOKEN=your_replicate_token

# Blockchain Keys
DEPLOYER_PRIVATE_KEY=0x...  # Your private key
ORACLE_PRIVATE_KEY=0x...    # Same or different key

# Arkiv
ARKIV_PRIVATE_KEY=0x...     # Arkiv account

# Network URLs (defaults are fine)
PASEO_RPC_URL=https://testnet-passet-hub-eth-rpc.polkadot.io
KUSAMA_RPC_URL=https://kusama-asset-hub-eth-rpc.polkadot.io
ARKIV_RPC_URL=https://mendoza.hoodi.arkiv.network/rpc
ARKIV_WS_URL=wss://mendoza.hoodi.arkiv.network/rpc/ws
```

### 2. Get Testnet Tokens

**For Paseo Testnet:**
1. Go to https://faucet.polkadot.io/
2. Select "Paseo Testnet"
3. Enter your Ethereum address (from DEPLOYER_PRIVATE_KEY)
4. Request tokens

**Check Balance:**
```bash
# You'll see balance when you try to deploy
```

---

## 🏠 Local Testing

### Step 1: Start Local Hardhat Node

```bash
cd contracts
npx hardhat node
```

Keep this terminal open.

### Step 2: Deploy Contract Locally

```bash
cd backend
python deploy_contract_to_network.py --network local
```

**Expected Output:**
```
✅ CONTRACT DEPLOYED
   Contract: 0x5FbDB2315678afecb367f032d93F642f64180aa3
   Block: 1
💾 Contract address saved to contract_addresses.json
```

### Step 3: Deploy a Conspiracy

```bash
python deploy_conspiracy_to_network.py --network local --difficulty 4 --docs 5
```

**Expected Output:**
```
✅ GENERATION COMPLETE (~60s)
✅ CONVERSION COMPLETE
✅ BLOCKCHAIN REGISTRATION COMPLETE
✅ ARKIV UPLOAD COMPLETE
🎉 Conspiracy deployed to local!
```

---

## 🧪 Paseo Testnet Deployment

### Step 1: Get Testnet Tokens

1. Visit https://faucet.polkadot.io/
2. Select "Paseo Testnet"
3. Paste your address (derived from DEPLOYER_PRIVATE_KEY)
4. Click "Submit"
5. Wait ~30 seconds

### Step 2: Deploy Contract to Paseo

```bash
cd backend
python deploy_contract_to_network.py --network paseo
```

**What Happens:**
1. Checks your balance
2. Deploys InfiniteConspiracy contract
3. Saves address to `contract_addresses.json`

**Expected Output:**
```
╔==========================================================╗
║  DEPLOYING TO PASEO                                      ║
╚==========================================================╝

📌 Network: https://testnet-passet-hub-eth-rpc.polkadot.io
   Chain ID: 420420422

⚠️  This network requires funded accounts:
   Get testnet tokens: https://faucet.polkadot.io/

✅ DEPLOYER_PRIVATE_KEY found

🚀 Running hardhat deployment...
   Command: npx hardhat run scripts/deploy.js --network paseo
   
🚀 Deploying InfiniteConspiracy contract...

📋 Deployment Details:
  Network: paseo
  Deployer: 0x...
  Oracle: 0x...
  Deployer Balance: 10.0 KSM

⏳ Deploying contract...
✅ Contract deployed to: 0x...

✅ DEPLOYMENT SUCCESSFUL
   Contract: 0x...
   Block: 12345
   
💾 Contract address saved to contract_addresses.json

🎉 You can now deploy conspiracies to this network using:
   python deploy_conspiracy_to_network.py --network paseo
```

### Step 3: Deploy Conspiracies to Paseo

Now you can deploy multiple conspiracies **without redeploying the contract**:

```bash
# Deploy first conspiracy
python deploy_conspiracy_to_network.py --network paseo --difficulty 5 --docs 8

# Deploy second conspiracy (same contract)
python deploy_conspiracy_to_network.py --network paseo --difficulty 6 --docs 10

# Deploy third conspiracy (same contract)
python deploy_conspiracy_to_network.py --network paseo --difficulty 7 --docs 12
```

Each conspiracy:
- Uses the **same smart contract**
- Gets registered with a unique mystery ID
- Has its own bounty pool
- Is uploaded to Arkiv with network tags

### Step 4: Verify on Paseo

**Check Contract on Block Explorer:**
- Paseo Explorer: (if available)
- Look up your contract address

**Query Arkiv:**
```bash
python test_query_arkiv.py --filter 'network = "paseo"'
```
