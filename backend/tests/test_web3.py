#!/usr/bin/env python3
"""Test Web3 (Kusama) integration."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger
from blockchain import Web3Client


async def test_kusama_connection():
    """Test Kusama Web3 connection."""
    config = load_config()
    logger = setup_logger("test_web3", "INFO", config.log_dir)
    
    logger.info("="*60)
    logger.info("Testing Kusama Web3 Integration")
    logger.info("="*60)
    
    if not config.oracle_private_key:
        logger.error("❌ ORACLE_PRIVATE_KEY not set")
        return False
    
    if not config.contract_address:
        logger.warning("⚠️  CONTRACT_ADDRESS not set (skipping contract tests)")
        contract_address = None
    else:
        contract_address = config.contract_address
    
    try:
        # Initialize client (no contract for connection test)
        client = Web3Client(
            rpc_url=config.kusama_rpc_url,
            private_key=config.oracle_private_key,
            contract_address=contract_address or "0x0000000000000000000000000000000000000000",
            contract_abi_path=None  # Skip ABI loading for connection test
        )
        
        # Test 1: Connection
        logger.info("\nTest 1: Checking connection...")
        is_connected = await client.is_connected()
        if is_connected:
            logger.info("✅ Connected to Kusama Asset Hub")
        else:
            logger.error("❌ Failed to connect")
            return False
        
        # Test 2: Get balance
        logger.info("\nTest 2: Checking account balance...")
        balance = await client.get_balance()
        balance_ksm = client.w3.from_wei(balance, 'ether')
        logger.info(f"✅ Account: {client.address}")
        logger.info(f"✅ Balance: {balance_ksm} KSM (testnet)")
        
        if balance == 0:
            logger.warning("⚠️  Zero balance - you may need testnet tokens from faucet")
        
        logger.info("\n✅ All Web3 tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Web3 test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Run Web3 tests."""
    print("🧪 Web3 (Kusama) Test Suite")
    print("="*60)
    
    passed = await test_kusama_connection()
    
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Kusama Web3: {'✅ PASS' if passed else '❌ FAIL'}")
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

