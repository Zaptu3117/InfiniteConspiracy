# Contracts Overview

## Introduction

The Infinite Conspiracy smart contracts manage the on-chain game mechanics for the detective mystery game. Deployed on Kusama Asset Hub (Ethereum-compatible), the contracts handle player registration, mystery creation, answer submissions, bounty distribution, and leaderboards.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              KUSAMA ASSET HUB (EVM-Compatible)              │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        InfiniteConspiracy.sol Contract               │  │
│  │                                                       │  │
│  │  ┌────────────────┐  ┌────────────────┐            │  │
│  │  │ Player         │  │ Mystery        │            │  │
│  │  │ Management     │  │ Management     │            │  │
│  │  │                │  │                │            │  │
│  │  │ • Inscription  │  │ • Creation     │            │  │
│  │  │ • Stats        │  │ • Registration │            │  │
│  │  │ • Leaderboard  │  │ • Expiry       │            │  │
│  │  └────────────────┘  └────────────────┘            │  │
│  │                                                       │  │
│  │  ┌────────────────┐  ┌────────────────┐            │  │
│  │  │ Submission     │  │ Bounty         │            │  │
│  │  │ System         │  │ System         │            │  │
│  │  │                │  │                │            │  │
│  │  │ • Quadratic    │  │ • Accumulation │            │  │
│  │  │   Costs        │  │ • Distribution │            │  │
│  │  │ • Answer       │  │ • Treasury     │            │  │
│  │  │   Validation   │  │                │            │  │
│  │  └────────────────┘  └────────────────┘            │  │
│  │                                                       │  │
│  │  ┌────────────────┐  ┌────────────────┐            │  │
│  │  │ Proof          │  │ Access         │            │  │
│  │  │ System         │  │ Control        │            │  │
│  │  │                │  │                │            │  │
│  │  │ • Revelation   │  │ • Oracle Role  │            │  │
│  │  │ • Verification │  │ • Admin Role   │            │  │
│  │  └────────────────┘  └────────────────┘            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Smart Contract Components

### 1. Player Management

**Inscription System**:
- One-time 10 KSM fee to become a player
- Sybil attack prevention
- Stats tracking (mysteries solved, bounty won, reputation)
- On-chain leaderboard

**Player Stats**:
```solidity
struct PlayerStats {
    bool inscribed;              // Whether player is registered
    uint256 mysteriesSolved;     // Total mysteries solved
    uint256 totalBountyWon;      // Total KSM won
    uint256 totalSubmissions;    // Total answer attempts
    uint256 reputation;          // Reputation points
    uint256 inscriptionTime;     // Registration timestamp
}
```

### 2. Mystery Management

**Mystery Creation** (Oracle Only):
- Register new mysteries on-chain
- Store answer hash (no plaintext!)
- Store proof hash (for later revelation)
- Set difficulty and expiry
- Initial bounty allocation

**Mystery Structure**:
```solidity
struct Mystery {
    bytes32 mysteryId;      // Unique identifier (keccak256)
    bytes32 answerHash;     // Keccak256 of correct answer (lowercase)
    bytes32 proofHash;      // Keccak256 of proof tree JSON
    uint256 bountyPool;     // Accumulated bounty (wei)
    uint256 createdAt;      // Creation timestamp
    uint256 expiresAt;      // Expiry timestamp
    uint8 difficulty;       // 1-10
    bool solved;            // Whether mystery is solved
    address solver;         // Winner address (if solved)
    bool proofRevealed;     // Whether proof has been revealed
    string proofData;       // Proof tree JSON (after revelation)
}
```

### 3. Submission System

**Quadratic Costs**:
- First submission: 1 KSM
- Second: 2 KSM (1 + 1²)
- Third: 5 KSM (1 + 2²)
- Fourth: 17 KSM (1 + 4²)
- Formula: `BASE_FEE + (submission_count²) * 1 KSM`

**Answer Validation**:
- Normalize answer (lowercase, trim)
- Hash with keccak256
- Compare with stored hash
- No plaintext answers on-chain

**Four-Part Answer Format** (for conspiracy mysteries):
```
WHO | WHAT | WHERE | WHY
```

All parts are lowercased and concatenated with `|` delimiter before hashing.

### 4. Bounty System

**Bounty Accumulation**:
```
Initial Bounty (from oracle) = 10 KSM
+ (50% of all inscription fees)
+ (100% of all submission fees)
= Total Bounty Pool
```

**Distribution**:
- Winner gets 100% of bounty pool
- Bounty transferred immediately upon correct answer
- Reputation boost: 100 × difficulty

**Treasury**:
- 50% of inscription fees
- Used for mystery pool seeding
- Accumulates for platform sustainability

### 5. Proof System

**Proof Revelation**:
- After mystery solved OR expired
- Oracle reveals proof tree JSON
- Stored on-chain for transparency
- Proves mystery was solvable

**Verification**:
- Proof hash must match stored hash
- Immutable once stored
- Shows reasoning steps
- Demonstrates multi-hop solvability

### 6. Access Control

**Roles**:
- **DEFAULT_ADMIN_ROLE**: Contract admin, can grant/revoke roles
- **ORACLE_ROLE**: Can create mysteries and reveal proofs

**Oracle Responsibilities**:
- Generate mysteries
- Register on-chain with hashes
- Reveal proofs after expiry
- Cannot change answers after creation

## Data Flow

### Player Inscription Flow

```
1. Player calls inscribePlayer() with 10 KSM
   ↓
2. Contract validates:
   - Sufficient payment
   - Not already inscribed
   ↓
3. Create PlayerStats entry
   ↓
4. Add to leaderboard array
   ↓
5. Split fee:
   - 50% → Treasury
   - 50% → Active mystery pools (divided equally)
   ↓
6. Emit PlayerInscribed event
```

### Mystery Creation Flow

```
1. Backend generates mystery
   ↓
2. Generate answer hash: keccak256(lowercase(answer))
   ↓
3. Generate proof hash: keccak256(JSON.stringify(proof_tree))
   ↓
4. Oracle calls createMystery() with:
   - mysteryId (bytes32)
   - answerHash (bytes32)
   - proofHash (bytes32)
   - duration (uint256)
   - difficulty (uint8)
   - Initial bounty (msg.value)
   ↓
5. Contract creates Mystery struct
   ↓
6. Add to activeMysteries array
   ↓
7. Emit MysteryCreated event
```

### Answer Submission Flow

```
1. Player calls submitAnswer() with:
   - mysteryId (bytes32)
   - who (string)
   - what (string)
   - where (string)
   - why (string)
   - Payment (quadratic cost)
   ↓
2. Contract validates:
   - Player is inscribed
   - Mystery not solved
   - Mystery not expired
   - Sufficient payment
   ↓
3. Increment submission counters
   ↓
4. Add payment to bounty pool
   ↓
5. Emit AnswerSubmitted event
   ↓
6. Normalize and hash answer:
   hash = keccak256(lower(who) + "|" + lower(what) + "|" + lower(where) + "|" + lower(why))
   ↓
7. Compare with mystery.answerHash
   ↓
8. If CORRECT:
   ├─ Mark mystery as solved
   ├─ Transfer entire bounty pool to player
   ├─ Update player stats (solved++, bountyWon++, reputation++)
   ├─ Move mystery to solvedMysteries array
   ├─ Update leaderboard
   └─ Emit MysterySolved event
   ↓
9. If WRONG:
   └─ Transaction completes (player loses submission fee)
```

### Proof Revelation Flow

```
1. Mystery solved OR expired
   ↓
2. Oracle calls revealProof() with:
   - mysteryId (bytes32)
   - proof (string, JSON)
   ↓
3. Contract validates:
   - Mystery solved or expired
   - Proof not already revealed
   - keccak256(proof) == mystery.proofHash
   ↓
4. Store proof data on-chain
   ↓
5. Set proofRevealed = true
   ↓
6. Emit ProofRevealed event
```

## Technology Stack

### Smart Contract
- **Solidity 0.8.20** - Contract language
- **OpenZeppelin 5.0.0** - Security libraries
  - AccessControl - Role-based permissions
  - ReentrancyGuard - Reentrancy protection

### Development Tools
- **Hardhat 2.19.0** - Development framework
- **Hardhat Toolbox** - Testing utilities
- **dotenv** - Environment variables

### Network
- **Kusama Asset Hub** - EVM-compatible Layer 1
- **Chain ID**: 420420418 (mainnet), 420420422 (testnet)
- **Native Token**: KSM

## Key Features

### Security

1. **Reentrancy Protection**: All financial functions protected
2. **Access Control**: Oracle role for sensitive operations
3. **Answer Security**: Hashed answers, no plaintext
4. **Proof Integrity**: Immutable proof hashes
5. **Quadratic Costs**: Spam prevention

### Economics

1. **Inscription Fee**: 10 KSM (50/50 split)
2. **Submission Costs**: Quadratic (1 + n²)
3. **Bounty Accumulation**: Inscriptions + Submissions
4. **Winner Takes All**: 100% bounty to solver
5. **Reputation System**: Based on difficulty

### Transparency

1. **On-Chain Proof**: Proof trees revealed
2. **Public Stats**: Player stats visible
3. **Leaderboard**: Reputation-based ranking
4. **Event Logs**: All actions logged
5. **Open Source**: Contract code public

## Gas Costs

Estimated gas costs on Kusama Asset Hub:

| Operation | Gas Usage | Est. Cost (KSM) |
|-----------|-----------|-----------------|
| inscribePlayer() | ~100,000 | ~0.01 KSM + 10 KSM fee |
| submitAnswer() | ~150,000 | ~0.015 KSM + submission fee |
| createMystery() | ~200,000 | ~0.02 KSM |
| revealProof() | ~100,000 | ~0.01 KSM |

*Note: Gas prices may vary based on network congestion*

## Limitations

### Current Limitations

1. **Single Answer Format**: Only supports 4-part answers
2. **No Mystery Updates**: Cannot update after creation
3. **Simple Leaderboard**: Basic bubble sort (inefficient for large lists)
4. **No Time Extensions**: Cannot extend mystery duration
5. **No Partial Refunds**: Submission fees non-refundable

### Future Enhancements

1. **Multiple Answer Formats**: Support different answer structures
2. **Mystery Marketplace**: Player-created mysteries
3. **NFT Rewards**: Mint NFTs for top solvers
4. **Efficient Leaderboard**: Use off-chain indexing
5. **Time Extensions**: Allow oracle to extend mysteries
6. **Team Submissions**: Multiple players collaborate

## Integration Points

### Backend Integration

Backend calls these functions:
- `createMystery()` - Register new mystery
- `revealProof()` - Reveal proof after expiry

### Frontend Integration

Frontend reads these functions:
- `getActiveMysteries()` - List active mysteries
- `getMystery()` - Get mystery details
- `getPlayerStats()` - Get player stats
- `getLeaderboard()` - Get top players
- `getSubmissionCost()` - Calculate next submission cost

Frontend calls these functions:
- `inscribePlayer()` - Register as player
- `submitAnswer()` - Submit answer attempt

## Next Steps

- [Installation](./INSTALLATION.md) - Set up development environment
- [Deployment](./DEPLOYMENT.md) - Deploy contracts
- [Contract Reference](./CONTRACT_REFERENCE.md) - Complete API reference
- [Game Mechanics](./GAME_MECHANICS.md) - How the game works
- [Integration Guide](./INTEGRATION.md) - Integrate with frontend/backend



