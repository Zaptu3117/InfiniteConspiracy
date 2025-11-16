"""
Deploy InfiniteConspiracy contract to a specific network and store the address.

Usage:
    # Local hardhat
    python deploy_contract_to_network.py --network local
    
    # Paseo testnet
    python deploy_contract_to_network.py --network paseo
    
    # Kusama mainnet
    python deploy_contract_to_network.py --network kusama
"""

import asyncio
import argparse
import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_network_config(network: str):
    """Get network configuration."""
    configs = {
        "local": {
            "rpc_url": os.getenv("LOCAL_RPC_URL", "http://localhost:8545"),
            "hardhat_network": "localhost",
            "chain_id": 1337,
            "requires_funding": False
        },
        "paseo": {
            "rpc_url": os.getenv("PASEO_RPC_URL", "https://testnet-passet-hub-eth-rpc.polkadot.io"),
            "hardhat_network": "paseo",
            "chain_id": 420420422,
            "requires_funding": True,
            "faucet": "https://faucet.polkadot.io/"
        },
        "kusama": {
            "rpc_url": os.getenv("KUSAMA_RPC_URL", "https://kusama-asset-hub-eth-rpc.polkadot.io"),
            "hardhat_network": "kusama",
            "chain_id": 420420418,
            "requires_funding": True,
            "warning": "⚠️  MAINNET - Real funds will be used!"
        }
    }
    
    return configs.get(network)


async def deploy_contract(network: str):
    """Deploy contract using hardhat and store address."""
    
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + f"  DEPLOYING TO {network.upper()}" + " "*(48-len(network)) + "║")
    logger.info("╚" + "="*58 + "╝")
    logger.info("")
    
    # Get network config
    config = get_network_config(network)
    if not config:
        logger.error(f"❌ Unknown network: {network}")
        logger.info("   Available networks: local, paseo, kusama")
        return None
    
    # Check for mainnet warning
    if config.get("warning"):
        logger.warning(config["warning"])
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Deployment cancelled.")
            return None
    
    # Check for funding requirement
    if config.get("requires_funding"):
        logger.info(f"📌 Network: {config['rpc_url']}")
        logger.info(f"   Chain ID: {config['chain_id']}")
        logger.info("")
        logger.info("⚠️  This network requires funded accounts:")
        logger.info(f"   Get testnet tokens: {config.get('faucet', 'N/A')}")
        logger.info("")
        
        deployer_key = os.getenv("DEPLOYER_PRIVATE_KEY")
        if not deployer_key:
            logger.error("❌ DEPLOYER_PRIVATE_KEY not set in .env")
            return None
        
        logger.info("✅ DEPLOYER_PRIVATE_KEY found")
        logger.info("")
    
    # Run hardhat deployment
    logger.info("🚀 Running hardhat deployment...")
    logger.info("")
    
    contracts_dir = Path(__file__).parent.parent / "contracts"
    
    try:
        # Build hardhat command
        cmd = ["npx", "hardhat", "run", "scripts/deploy.js"]
        if network != "local":
            cmd.extend(["--network", config["hardhat_network"]])
        
        logger.info(f"   Command: {' '.join(cmd)}")
        logger.info(f"   Working directory: {contracts_dir}")
        logger.info("")
        
        result = subprocess.run(
            cmd,
            cwd=contracts_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )
        
        if result.returncode != 0:
            logger.error("❌ Deployment failed:")
            logger.error(result.stderr)
            return None
        
        logger.info(result.stdout)
        
        # Read deployment info from contracts/deployment.json
        deployment_file = contracts_dir / "deployment.json"
        if not deployment_file.exists():
            logger.error("❌ deployment.json not found")
            return None
        
        with open(deployment_file, 'r') as f:
            deployment_info = json.load(f)
        
        logger.info("")
        logger.info("✅ DEPLOYMENT SUCCESSFUL")
        logger.info(f"   Contract: {deployment_info['contract']}")
        logger.info(f"   Deployer: {deployment_info['deployer']}")
        logger.info(f"   Oracle: {deployment_info['oracle']}")
        logger.info(f"   Block: {deployment_info['blockNumber']}")
        logger.info("")
        
        # Store in contract_addresses.json
        addresses_file = Path(__file__).parent / "contract_addresses.json"
        
        if addresses_file.exists():
            with open(addresses_file, 'r') as f:
                addresses = json.load(f)
        else:
            addresses = {}
        
        addresses[network] = {
            "address": deployment_info["contract"],
            "deployed_at": deployment_info["deployedAt"],
            "deployer": deployment_info["deployer"],
            "oracle": deployment_info["oracle"],
            "network": deployment_info["network"],
            "block_number": deployment_info["blockNumber"],
            "rpc_url": config["rpc_url"]
        }
        
        with open(addresses_file, 'w') as f:
            json.dump(addresses, f, indent=2)
        
        logger.info("💾 Contract address saved to contract_addresses.json")
        logger.info("")
        logger.info("🎉 You can now deploy conspiracies to this network using:")
        logger.info(f"   python test_full_e2e_with_contract.py --network {network}")
        logger.info("")
        
        return addresses[network]
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Deployment timed out (5 minutes)")
        return None
    except Exception as e:
        logger.error(f"❌ Deployment error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Deploy contract to network')
    parser.add_argument(
        '--network',
        choices=['local', 'paseo', 'kusama'],
        required=True,
        help='Network to deploy to'
    )
    
    args = parser.parse_args()
    
    result = await deploy_contract(args.network)
    
    if result:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

