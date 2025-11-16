# 🚀 Deployment System Overview

## 📁 Files Created

### Contract Address Management
- **`contract_addresses.json`** - Stores deployed contract addresses for each network
  - Prevents redeploying contracts unnecessarily
  - Tracks deployer, oracle, block number

### Deployment Scripts

1. **`deploy_contract_to_network.py`** - Deploy contract to a network (ONE TIME)
   ```bash
   python deploy_contract_to_network.py --network paseo
   ```
   - Deploys InfiniteConspiracy contract
   - Saves address to `contract_addresses.json`
   - Only needs to be run once per network

2. **`deploy_conspiracy_to_network.py`** - Deploy conspiracy to existing contract (MULTIPLE TIMES)
   ```bash
   python deploy_conspiracy_to_network.py --network paseo --difficulty 5 --docs 10
   ```
   - Loads contract address from `contract_addresses.json`
   - Generates conspiracy
   - Registers on blockchain
   - Uploads to Arkiv
   - Can be run many times with same contract

3. **`tests/test_blockchain_only.py`** - Test blockchain with dummy data
   ```bash
   python tests/test_blockchain_only.py --contract 0x...
   ```

4. **`tests/test_full_e2e_with_contract.py`** - Full e2e with contract
   ```bash
   python tests/test_full_e2e_with_contract.py --contract 0x...
   ```

### Documentation
- **`TESTNET_DEPLOYMENT_GUIDE.md`** - Complete deployment guide for all networks
- **`ENV_VARIABLES_GUIDE.md`** - Environment configuration reference

---

## 🔄 Deployment Workflow

### First Time Setup (Per Network)

```bash
# 1. Deploy contract to network (ONCE)
cd backend
python deploy_contract_to_network.py --network paseo

# Output:
# ✅ Contract deployed to: 0xABC...
# 💾 Saved to contract_addresses.json
```

### Deploy Conspiracies (Many Times)

```bash
# 2. Deploy multiple conspiracies using same contract
python deploy_conspiracy_to_network.py --network paseo --difficulty 5 --docs 8
python deploy_conspiracy_to_network.py --network paseo --difficulty 6 --docs 10
python deploy_conspiracy_to_network.py --network paseo --difficulty 7 --docs 12

# Each conspiracy:
# - Uses stored contract address
# - Gets unique mystery ID
# - Has own bounty pool
# - Tagged with network in Arkiv
```

---

## 🌐 Supported Networks

### 🏠 Local (Hardhat)
```bash
# Start node
cd contracts && npx hardhat node

# Deploy contract
python deploy_contract_to_network.py --network local

# Deploy conspiracies
python deploy_conspiracy_to_network.py --network local
```

### 🧪 Paseo Testnet
```bash
# Get testnet tokens
# https://faucet.polkadot.io/

# Deploy contract
python deploy_contract_to_network.py --network paseo

# Deploy conspiracies
python deploy_conspiracy_to_network.py --network paseo --difficulty 5 --docs 10
```

### 🔴 Kusama Mainnet (Requires Confirmation)
```bash
# Deploy contract (asks for confirmation)
python deploy_contract_to_network.py --network kusama

# Deploy conspiracies (asks for confirmation)
python deploy_conspiracy_to_network.py --network kusama --difficulty 7 --docs 15
```

---

## 📊 Contract Address Storage

**`contract_addresses.json` structure:**
```json
{
  "local": {
    "address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "deployed_at": "2025-11-16T12:37:21.696Z",
    "deployer": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "oracle": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "network": "localhost",
    "block_number": 1,
    "rpc_url": "http://localhost:8545"
  },
  "paseo": {
    "address": "0x...",
    "deployed_at": "2025-11-16T...",
    ...
  },
  "kusama": {
    "address": "",
    ...
  }
}
```

---

## 🎯 Key Features

### ✅ Contract Reuse
- Deploy contract **once per network**
- Register **unlimited conspiracies** to same contract
- Each conspiracy tracked independently

### ✅ Network Isolation
- Separate contracts for local/paseo/kusama
- Arkiv documents tagged with network
- Query by network: `network = "paseo"`

### ✅ Safety Features
- Mainnet deployment requires confirmation
- Balance checking before deployment
- Automatic testnet faucet links

### ✅ Full Integration
- Blockchain: Mystery registration with bounties
- Arkiv: Document storage with semantic search
- Validation: Automated multi-hop testing

---

## 🔍 Querying Deployed Conspiracies

### Query by Network
```python
# All Paseo conspiracies
query.where(eq("network", "paseo"))

# Active Paseo conspiracies
query.where(eq("network", "paseo"))
     .where(eq("status", "active"))

# Specific difficulty on Paseo
query.where(eq("network", "paseo"))
     .where(eq("difficulty", "5"))
```

### Query by Contract
```python
# All conspiracies for a specific contract
query.where(eq("contract_address", "0xABC..."))
```

---

## 📈 Production Workflow

### Development Phase
```bash
# Test locally
python deploy_contract_to_network.py --network local
python deploy_conspiracy_to_network.py --network local --difficulty 4 --docs 5
```

### Testnet Phase
```bash
# Deploy to Paseo
python deploy_contract_to_network.py --network paseo
python deploy_conspiracy_to_network.py --network paseo --difficulty 5 --docs 10
# Test thoroughly...
```

### Production Phase
```bash
# Deploy to Kusama mainnet
python deploy_contract_to_network.py --network kusama
python deploy_conspiracy_to_network.py --network kusama --difficulty 7 --docs 15 --env prod
```

---

## 🎉 What's Working

✅ Smart contract compilation and deployment
✅ Contract address persistence
✅ Multi-network support (local/paseo/kusama)
✅ Conspiracy generation pipeline
✅ Blockchain registration with bounties
✅ Arkiv document upload
✅ Full end-to-end testing
✅ Network-tagged queries

**Ready for testnet deployment!** 🚀

