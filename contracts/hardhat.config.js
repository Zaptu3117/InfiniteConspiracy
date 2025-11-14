require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {
      chainId: 1337
    },
    // Kusama Asset Hub Mainnet (Ethereum-compatible smart contracts)
    kusama: {
      url: process.env.KUSAMA_RPC_URL || "https://kusama-asset-hub-eth-rpc.polkadot.io",
      accounts: process.env.DEPLOYER_PRIVATE_KEY ? [process.env.DEPLOYER_PRIVATE_KEY] : [],
      chainId: 420420418  // Kusama Asset Hub Chain ID
    },
    // Paseo Testnet (Recommended for development)
    paseo: {
      url: process.env.KUSAMA_RPC_URL || "https://testnet-passet-hub-eth-rpc.polkadot.io",
      accounts: process.env.DEPLOYER_PRIVATE_KEY ? [process.env.DEPLOYER_PRIVATE_KEY] : [],
      chainId: 420420422  // Paseo Testnet Chain ID
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};

