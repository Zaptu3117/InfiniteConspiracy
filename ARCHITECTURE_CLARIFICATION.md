# Architecture Clarification: Dual Network Design

## 🏗️ Two Separate Networks

**Important:** This project uses TWO independent networks, each serving a specific purpose:

### 1. Arkiv Mendoza (Data Layer)
**Purpose:** Decentralized storage for mystery content

**What it stores:**
- Mystery documents (JSON format)
- Generated images (PNG files)
- Mystery metadata
- All queryable with 7-day TTL

**Endpoint:**
- RPC: `https://mendoza.hoodi.arkiv.network/rpc`
- SDK: Arkiv SDK v1.0.0a5

**Used by:**
- Backend: Push mystery data after generation
- Frontend: Query and retrieve documents/images

---

### 2. Kusama Asset Hub (Blockchain)
**Purpose:** Ethereum-compatible smart contracts for game logic

**What it handles:**
- InfiniteConspiracy.sol contract
- Player inscriptions (10 KSM fee)
- Mystery registration with bounties
- Answer submissions with quadratic costs
- Bounty distribution to winners
- On-chain leaderboard

**Endpoints:**
- **Testnet (Paseo)**: `https://testnet-passet-hub-eth-rpc.polkadot.io`
  - Chain ID: `420420422`
  - Recommended for development
  
- **Mainnet (Kusama Hub)**: `https://kusama-asset-hub-eth-rpc.polkadot.io`
  - Chain ID: `420420418`
  - Production deployment

**Used by:**
- Backend: Register mysteries on-chain
- Smart contracts: Solidity 0.8.20 with Hardhat
- Frontend: Submit answers, check bounties

---

## 🔄 Data Flow

### Mystery Generation Flow
```
1. Backend generates mystery (Python + LLM)
   ↓
2. Push to Arkiv (documents + images)
   ↓
3. Register on Kusama (hashes + bounty)
   ↓
4. Frontend queries both:
   - Arkiv: Get mystery content
   - Kusama: Check bounty/status
```

### Player Flow
```
1. Player inscribes (Kusama contract)
   ↓
2. Frontend queries Arkiv for mystery
   ↓
3. Player investigates documents
   ↓
4. Submit answer to Kusama contract
   ↓
5. If correct, win bounty from Kusama
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Arkiv (Data Layer)
ARKIV_RPC_URL=https://mendoza.hoodi.arkiv.network/rpc
ARKIV_PRIVATE_KEY=0x...

# Kusama (Blockchain)
KUSAMA_RPC_URL=https://testnet-passet-hub-eth-rpc.polkadot.io
KUSAMA_CHAIN_ID=420420422
ORACLE_PRIVATE_KEY=0x...
CONTRACT_ADDRESS=0x...
```

### Hardhat Deployment

```javascript
// Deploy to Paseo testnet (recommended)
npx hardhat run scripts/deploy.js --network paseo

// Deploy to Kusama mainnet (production)
npx hardhat run scripts/deploy.js --network kusama
```

---

## 🎯 Why Two Networks?

### Arkiv Strengths:
- ✅ Cheap storage for large documents/images
- ✅ Built-in TTL (mysteries auto-expire)
- ✅ Queryable with filters
- ✅ No gas fees for reads

### Kusama Strengths:
- ✅ Financial transactions (KSM bounties)
- ✅ Immutable proof/answer hashes
- ✅ Smart contract logic (quadratic costs)
- ✅ Trustless bounty distribution

### Why Not Just One?

**If only Arkiv:**
- ❌ No native token for bounties
- ❌ No smart contract logic
- ❌ No financial incentive layer

**If only Kusama:**
- ❌ Expensive to store 20+ documents on-chain
- ❌ Images would bloat blockchain
- ❌ Reading documents costs gas

**Together:** Best of both worlds! 🎉

---

## 🔐 Security Model

### Arkiv Security:
- Documents are **public but unspoiled**
- No proof tree or answer revealed
- Only metadata annotations for queries
- Clues scattered across documents

### Kusama Security:
- Answer stored as **SHA256 hash**
- Proof tree stored as **hash** until reveal
- Bounty pool **immutable** once created
- Winner verification **on-chain**

---

## 🚀 Deployment Checklist

### 1. Deploy Smart Contract (Kusama)
```bash
cd contracts
npm install
npx hardhat compile
npx hardhat run scripts/deploy.js --network paseo
# Save CONTRACT_ADDRESS to .env
```

### 2. Generate Mystery (Backend)
```bash
cd backend
uv pip install -e .
cp env.example .env
# Add all API keys to .env
python scripts/generate_mystery.py --mode llm
```

### 3. Push to Arkiv
```bash
python scripts/push_to_arkiv.py <mystery_id>
```

### 4. Register on Kusama
```bash
python scripts/register_on_chain.py <mystery_id>
```

### 5. Verify Both
- **Arkiv**: Query entities with mystery_id
- **Kusama**: Call getMystery() on contract

---

## 📚 Resources

### Arkiv Documentation
- Docs: https://docs.arkiv.network
- SDK: https://github.com/arkiv-network/sdk
- Faucet: (Get test tokens for Mendoza)

### Kusama Documentation
- Kusama Smart Contracts: https://kusama.network/contracts
- Hardhat Guide: https://docs.polkadot.network/develop/smart-contracts
- Paseo Explorer: https://blockscout-passet-hub.parity-testnet.parity.io

---

## ❓ FAQ

**Q: Can I use just Arkiv without Kusama?**
A: For testing, yes. But the full game requires both for bounty mechanics.

**Q: Can I deploy to different Kusama networks?**
A: Yes! Use `paseo` for testnet, `kusama` for mainnet in Hardhat.

**Q: Do I need separate keys for Arkiv and Kusama?**
A: Yes, technically two networks. You can use same key but recommended to separate.

**Q: What if Arkiv data expires before mystery solved?**
A: Set appropriate TTL (default 7 days). Mystery still registered on Kusama, just no accessible documents.

**Q: Can frontend query both networks?**
A: Yes! Frontend uses Arkiv SDK for documents and Web3 for Kusama contract calls.

---

**Last Updated:** Based on implementation with Arkiv SDK v1.0.0a5 and Kusama Asset Hub preview release.

