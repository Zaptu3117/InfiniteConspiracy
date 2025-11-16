# Smart Contract Documentation

## InfiniteConspiracy.sol

Complete smart contract for the Infinite Conspiracy game mechanics.

## Contract Address

```
Network: Kusama Testnet (Paseo)
Address: [To be deployed]
```

## Overview

The contract handles:
- **Player inscription** with fee split
- **Mystery registration** by oracle
- **Answer submission** with quadratic costs
- **Bounty distribution** to winners
- **Leaderboard** with reputation
- **Proof revelation** after expiry

## Constants

```solidity
uint256 public constant INSCRIPTION_FEE = 10 ether;      // 10 KSM
uint256 public constant BASE_SUBMISSION_FEE = 1 ether;   // 1 KSM
```

## Data Structures

### Mystery

```solidity
struct Mystery {
    bytes32 mysteryId;      // Keccak256 hash of mystery ID string
    bytes32 answerHash;     // Keccak256 hash of answer (lowercase)
    bytes32 proofHash;      // Keccak256 hash of proof tree JSON
    uint256 bountyPool;     // Accumulated bounty (wei)
    uint256 createdAt;      // Block timestamp
    uint256 expiresAt;      // Expiry timestamp
    uint8 difficulty;       // 1-10
    bool solved;            // Whether solved
    address solver;         // Winner address
    bool proofRevealed;     // Whether proof revealed
    string proofData;       // Proof tree JSON (after reveal)
}
```

### PlayerStats

```solidity
struct PlayerStats {
    bool inscribed;              // Whether player is inscribed
    uint256 mysteriesSolved;     // Total mysteries solved
    uint256 totalBountyWon;      // Total bounty won (wei)
    uint256 totalSubmissions;    // Total submissions across all mysteries
    uint256 reputation;          // Reputation points
    uint256 inscriptionTime;     // When inscribed
}
```

## Functions

### Player Functions

#### inscribePlayer()

```solidity
function inscribePlayer() external payable nonReentrant
```

**Purpose**: Register as a player to participate in mysteries

**Requirements**:
- Must send at least `INSCRIPTION_FEE` (10 KSM)
- Player not already inscribed

**Effects**:
- Creates `PlayerStats` entry
- Adds player to leaderboard
- Splits fee:
  - 50% → Treasury
  - 50% → Active mystery pools (divided equally)

**Example**:
```javascript
await contract.inscribePlayer({ value: ethers.parseEther("10") })
```

#### submitAnswer()

```solidity
function submitAnswer(bytes32 mysteryId, string calldata answer) 
    external 
    payable 
    nonReentrant
```

**Purpose**: Submit an answer attempt for a mystery

**Parameters**:
- `mysteryId`: Bytes32 hash of mystery ID
- `answer`: Answer string

**Cost**: Quadratic based on previous submissions
```
Cost = BASE_SUBMISSION_FEE + (submissions² × 1 KSM)

1st attempt: 1 KSM
2nd attempt: 2 KSM (1 + 1²)
3rd attempt: 5 KSM (1 + 2²)
4th attempt: 17 KSM (1 + 4²)
```

**Requirements**:
- Player is inscribed
- Mystery not solved
- Mystery not expired
- Sufficient payment

**Effects**:
- Increments submission counters
- Adds payment to bounty pool
- If correct: Solves mystery and pays bounty

**Example**:
```javascript
const mysteryId = ethers.keccak256(ethers.toUtf8Bytes("warehouse_leak_001"))
await contract.submitAnswer(
    mysteryId,
    "Sarah Martinez",
    { value: ethers.parseEther("1") }
)
```

### Oracle Functions

#### createMystery()

```solidity
function createMystery(
    bytes32 mysteryId,
    bytes32 answerHash,
    bytes32 proofHash,
    uint256 duration,
    uint8 difficulty
) external onlyRole(ORACLE_ROLE) payable
```

**Purpose**: Register a new mystery on-chain

**Parameters**:
- `mysteryId`: Keccak256(mystery_id_string)
- `answerHash`: Keccak256(lowercase(answer))
- `proofHash`: Keccak256(proof_tree_json)
- `duration`: Time until expiry (seconds)
- `difficulty`: 1-10

**Requirements**:
- Caller has `ORACLE_ROLE`
- Mystery ID not already used

**Effects**:
- Creates `Mystery` struct
- Adds to `activeMysteries` array
- Initial bounty from msg.value

**Example (Python)**:
```python
mystery_id_bytes = web3.solidity_keccak(['string'], [mystery_id])
answer_hash_bytes = web3.solidity_keccak(['string'], [answer.lower()])
proof_hash_bytes = web3.solidity_keccak(['string'], [json.dumps(proof_tree)])

tx = contract.functions.createMystery(
    mystery_id_bytes,
    answer_hash_bytes,
    proof_hash_bytes,
    604800,  # 7 days
    7        # difficulty
).transact({'value': web3.to_wei(10, 'ether')})
```

#### revealProof()

```solidity
function revealProof(bytes32 mysteryId, string calldata proof) 
    external 
    onlyRole(ORACLE_ROLE)
```

**Purpose**: Reveal proof tree after mystery expires or is solved

**Parameters**:
- `mysteryId`: Bytes32 hash of mystery ID
- `proof`: Proof tree JSON string

**Requirements**:
- Caller has `ORACLE_ROLE`
- Mystery expired OR solved
- Proof not already revealed
- Proof hash matches stored hash

**Effects**:
- Sets `proofRevealed = true`
- Stores proof data on-chain

**Example (Python)**:
```python
import json

proof_json = json.dumps(proof_tree, sort_keys=True)
mystery_id_bytes = web3.solidity_keccak(['string'], [mystery_id])

tx = contract.functions.revealProof(
    mystery_id_bytes,
    proof_json
).transact()
```

### View Functions

#### getLeaderboard()

```solidity
function getLeaderboard(uint256 limit) external view returns (
    address[] memory players,
    uint256[] memory reputations,
    uint256[] memory solvedCounts
)
```

**Purpose**: Get top players by reputation

**Returns**: Arrays of player addresses, reputations, and solve counts

**Example**:
```javascript
const [players, reps, solves] = await contract.getLeaderboard(10)
players.forEach((player, i) => {
    console.log(`${i+1}. ${player}: ${reps[i]} rep, ${solves[i]} solved`)
})
```

#### getPlayerStats()

```solidity
function getPlayerStats(address player) external view returns (PlayerStats memory)
```

**Purpose**: Get statistics for a specific player

**Example**:
```javascript
const stats = await contract.getPlayerStats(playerAddress)
console.log(`Solved: ${stats.mysteriesSolved}`)
console.log(`Bounty Won: ${ethers.formatEther(stats.totalBountyWon)} KSM`)
console.log(`Reputation: ${stats.reputation}`)
```

#### getMystery()

```solidity
function getMystery(bytes32 mysteryId) external view returns (Mystery memory)
```

**Purpose**: Get mystery data

**Example**:
```javascript
const mysteryIdBytes = ethers.keccak256(ethers.toUtf8Bytes("warehouse_leak_001"))
const mystery = await contract.getMystery(mysteryIdBytes)
console.log(`Bounty: ${ethers.formatEther(mystery.bountyPool)} KSM`)
console.log(`Solved: ${mystery.solved}`)
console.log(`Expires: ${new Date(mystery.expiresAt * 1000)}`)
```

#### getActiveMysteries()

```solidity
function getActiveMysteries() external view returns (bytes32[] memory)
```

**Purpose**: Get list of active (unsolved, unexpired) mysteries

**Example**:
```javascript
const activeMysteries = await contract.getActiveMysteries()
console.log(`${activeMysteries.length} active mysteries`)
```

#### getSubmissionCost()

```solidity
function getSubmissionCost(address player, bytes32 mysteryId) 
    external 
    view 
    returns (uint256)
```

**Purpose**: Calculate cost for next submission

**Example**:
```javascript
const cost = await contract.getSubmissionCost(playerAddress, mysteryIdBytes)
console.log(`Next submission cost: ${ethers.formatEther(cost)} KSM`)
```

## Events

### PlayerInscribed

```solidity
event PlayerInscribed(address indexed player, uint256 poolContribution)
```

Emitted when a player inscribes.

### MysteryCreated

```solidity
event MysteryCreated(bytes32 indexed mysteryId, uint256 bounty)
```

Emitted when oracle creates a mystery.

### AnswerSubmitted

```solidity
event AnswerSubmitted(bytes32 indexed mysteryId, address indexed player, uint256 cost)
```

Emitted when player submits an answer (correct or incorrect).

### MysterySolved

```solidity
event MysterySolved(bytes32 indexed mysteryId, address indexed solver, uint256 bounty)
```

Emitted when mystery is solved and bounty is paid.

### ProofRevealed

```solidity
event ProofRevealed(bytes32 indexed mysteryId, string proof)
```

Emitted when oracle reveals proof.

## Economics Flow

### Inscription

```
Player pays 10 KSM
    ↓
50% (5 KSM) → Treasury
50% (5 KSM) → Split among active mystery pools
```

### Submissions

```
Player pays (1 + n² KSM)
    ↓
100% → Mystery bounty pool
```

### Mystery Solution

```
Mystery bounty pool (Initial + Inscriptions + Submissions)
    ↓
100% → Winner (solver)
```

### Reputation

```
Reputation = 100 × mystery_difficulty

Solving difficulty 7 mystery: +700 reputation
Solving difficulty 10 mystery: +1000 reputation
```

## Security Features

### Reentrancy Protection

All state-changing financial functions use `nonReentrant` modifier.

### Access Control

- `ORACLE_ROLE` required for mystery creation/revelation
- `DEFAULT_ADMIN_ROLE` for admin functions

### Answer Validation

- Answers normalized to lowercase
- SHA256 hashed
- No plaintext answers on-chain

### Quadratic Costs

Prevents spam and brute-force attempts.

## Deployment

### Hardhat Script

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer, oracle] = await hre.ethers.getSigners();
  
  const InfiniteConspiracy = await hre.ethers.getContractFactory("InfiniteConspiracy");
  const contract = await InfiniteConspiracy.deploy(oracle.address);
  
  await contract.waitForDeployment();
  console.log("Contract deployed to:", await contract.getAddress());
}

main().catch(console.error);
```

### Deploy Command
```bash
cd contracts
npx hardhat run scripts/deploy.js --network kusama
```

## Integration Examples

### Frontend (ethers.js)
```javascript
import { ethers } from 'ethers';

// Connect to contract
const provider = new ethers.JsonRpcProvider(RPC_URL);
const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider);

// Get active mysteries
const activeMysteries = await contract.getActiveMysteries();

// Get leaderboard
const [players, reps, solves] = await contract.getLeaderboard(10);

// Submit answer (with signer)
const signer = await provider.getSigner();
const contractWithSigner = contract.connect(signer);

const mysteryId = ethers.keccak256(ethers.toUtf8Bytes("mystery_001"));
const cost = await contract.getSubmissionCost(await signer.getAddress(), mysteryId);

await contractWithSigner.submitAnswer(
    mysteryId,
    "John Doe",
    { value: cost }
);
```

### Backend (web3.py)

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# Register mystery
mystery_id_bytes = w3.solidity_keccak(['string'], [mystery_id])
answer_hash = w3.solidity_keccak(['string'], [answer.lower()])
proof_hash = w3.solidity_keccak(['string'], [json.dumps(proof_tree)])

tx = contract.functions.createMystery(
    mystery_id_bytes,
    answer_hash,
    proof_hash,
    604800,
    7
).build_transaction({
    'from': oracle_address,
    'nonce': w3.eth.get_transaction_count(oracle_address),
    'value': w3.to_wei(10, 'ether')
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
```

---

**Next**: See [FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md) for UI integration.

