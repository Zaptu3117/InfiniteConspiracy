#!/usr/bin/env python3
"""Test Arkiv SDK integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger
from arkiv import ArkivClient


def test_arkiv_connection():
    """Test Arkiv client connection."""
    config = load_config()
    logger = setup_logger("test_arkiv", "INFO", config.log_dir)
    
    logger.info("="*60)
    logger.info("Testing Arkiv SDK Integration")
    logger.info("="*60)
    
    if not config.arkiv_private_key:
        logger.error("❌ ARKIV_PRIVATE_KEY not set")
        return False
    
    try:
        with ArkivClient(
            private_key=config.arkiv_private_key,
            rpc_url=config.arkiv_rpc_url,
            account_name="test_mystery_oracle"
        ) as client:
            logger.info("✅ Arkiv client initialized")
            
            # Test 1: Create a test entity
            logger.info("\nTest 1: Creating test entity...")
            test_data = b"Test entity for Arkiv integration"
            entity_key, _ = client.create_entity(
                payload=test_data,
                content_type="text/plain",
                attributes={"type": "test", "purpose": "integration_test"},
                btl=120  # 120 blocks TTL
            )
            logger.info(f"✅ Created entity: {entity_key}")
            
            # Test 2: Retrieve entity
            logger.info("\nTest 2: Retrieving entity...")
            entity = client.get_entity(entity_key)
            retrieved_data = (entity.payload or b"").decode("utf-8", errors="ignore")
            logger.info(f"✅ Retrieved data: {retrieved_data}")
            
            if retrieved_data != test_data.decode():
                logger.error("❌ Data mismatch!")
                return False
            
            # Test 3: Query entities
            logger.info("\nTest 3: Querying entities...")
            query = 'type = "test" and purpose = "integration_test"'
            entities = client.query_entities(query, limit=10)
            logger.info(f"✅ Found {len(entities)} test entities")
            
            logger.info("\n✅ All Arkiv tests passed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Arkiv test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Run Arkiv tests."""
    print("🧪 Arkiv SDK Test Suite")
    print("="*60)
    
    passed = test_arkiv_connection()
    
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Arkiv Integration: {'✅ PASS' if passed else '❌ FAIL'}")
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

