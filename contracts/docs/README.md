# Contracts Documentation

Smart contract documentation for Infinite Conspiracy on Kusama Asset Hub.

## Table of Contents

### Getting Started
- [Contracts Overview](./CONTRACTS_OVERVIEW.md) - System architecture
- [Installation](./INSTALLATION.md) - Setup and configuration  
- [Deployment Guide](./DEPLOYMENT.md) - Deploy to testnet/mainnet

### Smart Contract
- [InfiniteConspiracy Contract](./CONTRACT_REFERENCE.md) - Complete API reference
- [Game Mechanics](./GAME_MECHANICS.md) - How the game works on-chain
- [Economics](./ECONOMICS.md) - Fees, bounties, and rewards

### Development
- [Testing Guide](./TESTING.md) - Run tests and write new ones
- [Security](./SECURITY.md) - Security considerations
- [Integration Guide](./INTEGRATION.md) - Integrate with frontend/backend

### Network Information
- [Kusama Asset Hub](./KUSAMA_ASSET_HUB.md) - Network details
- [Testnet Guide](./TESTNET_GUIDE.md) - Using Paseo testnet

## Quick Links

### Common Tasks
- **Compile contracts**: `npx hardhat compile`
- **Run tests**: `npx hardhat test`
- **Deploy to testnet**: `npx hardhat run scripts/deploy.js --network paseo`
- **Deploy to mainnet**: `npx hardhat run scripts/deploy.js --network kusama`

### Important Files
- `contracts/InfiniteConspiracy.sol` - Main game contract
- `scripts/deploy.js` - Deployment script
- `test/InfiniteConspiracy.test.js` - Test suite
- `hardhat.config.js` - Hardhat configuration

## Contract Address

### Mainnet (Kusama Asset Hub)
- **Network**: Kusama Asset Hub
- **Chain ID**: 420420418
- **RPC**: https://kusama-asset-hub-eth-rpc.polkadot.io
- **Contract**: TBD (after deployment)

### Testnet (Paseo)
- **Network**: Paseo Testnet
- **Chain ID**: 420420422
- **RPC**: https://testnet-passet-hub-eth-rpc.polkadot.io
- **Contract**: TBD (after deployment)

## Documentation Status

📝 **New** - These docs are freshly written
- CONTRACTS_OVERVIEW.md
- INSTALLATION.md
- DEPLOYMENT.md
- CONTRACT_REFERENCE.md
- GAME_MECHANICS.md
- ECONOMICS.md
- TESTING.md
- SECURITY.md
- INTEGRATION.md
- KUSAMA_ASSET_HUB.md
- TESTNET_GUIDE.md

## Need Help?

1. Start with [CONTRACTS_OVERVIEW.md](./CONTRACTS_OVERVIEW.md) for system architecture
2. Follow [INSTALLATION.md](./INSTALLATION.md) to set up your environment
3. Read [DEPLOYMENT.md](./DEPLOYMENT.md) to deploy contracts
4. Check [CONTRACT_REFERENCE.md](./CONTRACT_REFERENCE.md) for API details
5. See [INTEGRATION.md](./INTEGRATION.md) for frontend/backend integration

## Contributing

When modifying contracts, please:
1. Update relevant documentation
2. Add/update tests
3. Run security checks
4. Update this README if adding new docs


