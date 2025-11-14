#!/usr/bin/env python3
"""
Push a generated mystery to Arkiv.

Usage:
    python scripts/push_to_arkiv.py <mystery_id>
    python scripts/push_to_arkiv.py warehouse_leak_001
"""

import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger
from models import Mystery
from arkiv import ArkivClient, ArkivPusher


def push_mystery_to_arkiv(mystery_id: str):
    """Push mystery to Arkiv (synchronous with context manager)."""
    logger = setup_logger("arkiv_pusher", "INFO", config.log_dir)
    
    logger.info("="*60)
    logger.info("🚀 PUSHING MYSTERY TO ARKIV")
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
    logger.info(f"   Question: {mystery.metadata.question}")
    logger.info(f"   Documents: {mystery.metadata.total_documents}")
    logger.info(f"   Images: {mystery.metadata.total_images}")
    logger.info("")
    
    # Check config
    if not config.validate():
        logger.error("❌ Configuration validation failed")
        return False
    
    # Create Arkiv client with context manager
    logger.info("🔌 Connecting to Arkiv...")
    logger.info(f"   RPC: {config.arkiv_rpc_url}")
    
    try:
        with ArkivClient(
            private_key=config.arkiv_private_key,
            rpc_url=config.arkiv_rpc_url,
            account_name="mystery_oracle"
        ) as client:
            logger.info("   ✅ Connected")
            logger.info("")
            
            # Create pusher
            pusher = ArkivPusher()
            
            # Push mystery
            images_dir = mystery_dir / "images"
            result = pusher.push_mystery(client, mystery, images_dir)
            
            logger.info("")
            logger.info("="*60)
            logger.info("✅ PUSH COMPLETE")
            logger.info("="*60)
            logger.info(f"Mystery ID: {result['mystery_id']}")
            logger.info(f"Total Entities: {result['total_entities']}")
            logger.info(f"  - Metadata: {result['metadata_entities']}")
            logger.info(f"  - Documents: {result['document_entities']}")
            logger.info(f"  - Images: {result['image_entities']}")
            logger.info("")
            
            # Verify
            logger.info("🔍 Verifying push...")
            verified = pusher.verify_push(client, mystery.metadata.mystery_id)
            
            if verified:
                logger.info("✅ Verification successful!")
            else:
                logger.error("❌ Verification failed")
                return False
            
            logger.info("")
            logger.info("Next step:")
            logger.info(f"  python scripts/register_on_chain.py {mystery_id}")
            logger.info("")
            
            return True
    
    except Exception as e:
        logger.error(f"❌ Arkiv error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Push mystery to Arkiv")
    parser.add_argument("mystery_id", help="Mystery ID (directory name)")
    args = parser.parse_args()
    
    # Note: No longer async - SDK v1.0.0a5 uses synchronous context manager
    success = push_mystery_to_arkiv(args.mystery_id)
    return 0 if success else 1


if __name__ == "__main__":
    from utils.config import config
    sys.exit(main())

