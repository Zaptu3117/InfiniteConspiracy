#!/usr/bin/env python3
"""
Register a mystery on the blockchain smart contract.

Usage:
    python scripts/register_on_chain.py <mystery_id> [--bounty 10.0]
    python scripts/register_on_chain.py warehouse_leak_001 --bounty 15.0
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger
from models import Mystery
from blockchain import Web3Client, MysteryRegistrar


async def register_mystery_on_chain(mystery_id: str, bounty_ksm: float = 10.0):
    """Register mystery on blockchain."""
    logger = setup_logger("chain_registrar", "INFO", config.log_dir)
    
    logger.info("="*60)
    logger.info("⛓️  REGISTERING MYSTERY ON BLOCKCHAIN")
    logger.info("="*60)
    logger.info("")
    
    # Load mystery
    mystery_dir = config.outputs_dir / "mysteries" / mystery_id
    mystery_file = mystery_dir / "mystery.json"
    
    if not mystery_file.exists():
        logger.error(f"❌ Mystery file not found: {mystery_file}")
        return False
    
    logger.info(f"📂 Loading mystery from {mystery_dir}")
    
    with open(mystery_file, 'r') as f:
        mystery_data = json.load(f)
    
    mystery = Mystery(**mystery_data)
    logger.info(f"   ✅ Loaded mystery: {mystery.metadata.mystery_id}")
    logger.info("")
    
    # Check config
    if not config.oracle_private_key:
        logger.error("❌ ORACLE_PRIVATE_KEY not set in .env")
        return False
    
    if not config.contract_address:
        logger.error("❌ CONTRACT_ADDRESS not set in .env")
        logger.error("   Deploy contract first: cd contracts && npx hardhat run scripts/deploy.js")
        return False
    
    # Create Web3 client
    logger.info("🔌 Connecting to blockchain...")
    logger.info(f"   RPC: {config.kusama_rpc_url}")
    logger.info(f"   Contract: {config.contract_address}")
    
    web3_client = Web3Client(
        rpc_url=config.kusama_rpc_url,
        private_key=config.oracle_private_key,
        contract_address=config.contract_address
    )
    
    if not web3_client.is_connected():
        logger.error("❌ Failed to connect to blockchain")
        return False
    
    logger.info(f"   ✅ Connected")
    logger.info(f"   Oracle Address: {web3_client.address}")
    
    balance = web3_client.get_balance()
    balance_ksm = balance / 10**18
    logger.info(f"   Balance: {balance_ksm:.4f} KSM")
    
    if balance_ksm < bounty_ksm:
        logger.error(f"❌ Insufficient balance for bounty (need {bounty_ksm} KSM)")
        return False
    
    logger.info("")
    
    # Create registrar
    registrar = MysteryRegistrar(web3_client)
    
    # Register mystery
    result = await registrar.register_mystery(mystery, bounty_ksm)
    
    if not result['success']:
        logger.error(f"❌ Registration failed: {result.get('error')}")
        return False
    
    logger.info("")
    logger.info("="*60)
    logger.info("✅ REGISTRATION COMPLETE")
    logger.info("="*60)
    logger.info(f"Mystery ID: {result['mystery_id']}")
    logger.info(f"Mystery ID (bytes32): 0x{result['mystery_id_bytes32']}")
    logger.info(f"Tx Hash: {result['tx_hash']}")
    logger.info(f"Block: {result['block_number']}")
    logger.info("")
    logger.info("🎮 Mystery is now live!")
    logger.info("   Players can start investigating")
    logger.info(f"   Bounty Pool: {bounty_ksm} KSM")
    logger.info(f"   Expires In: {mystery.metadata.expires_in} seconds ({mystery.metadata.expires_in // 86400} days)")
    logger.info("")
    
    # Verify on-chain
    logger.info("🔍 Verifying on-chain data...")
    on_chain_data = await registrar.get_mystery_on_chain(mystery.metadata.mystery_id)
    
    if on_chain_data:
        logger.info("   ✅ Mystery found on-chain")
        logger.info(f"   Difficulty: {on_chain_data['difficulty']}")
        logger.info(f"   Bounty Pool: {on_chain_data['bounty_pool'] / 10**18} KSM")
        logger.info(f"   Solved: {on_chain_data['solved']}")
    else:
        logger.error("   ❌ Mystery not found on-chain")
        return False
    
    logger.info("")
    logger.info("🎉 Setup complete! Mystery is ready for players.")
    logger.info("")
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Register mystery on blockchain")
    parser.add_argument("mystery_id", help="Mystery ID (directory name)")
    parser.add_argument("--bounty", type=float, default=10.0, help="Initial bounty in KSM")
    args = parser.parse_args()
    
    success = asyncio.run(register_mystery_on_chain(args.mystery_id, args.bounty))
    return 0 if success else 1


if __name__ == "__main__":
    from utils.config import config
    sys.exit(main())

