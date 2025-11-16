"""Generate conspiracy and push documents to Arkiv."""

import asyncio
import logging
import sys
import os
import json
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv()

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from narrative.conspiracy import ConspiracyPipeline
from utils import CerebrasClient
from arkiv_integration import ArkivClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def generate_and_push(environment: str = "dev"):
    """
    Generate conspiracy and push documents to Arkiv.
    
    Args:
        environment: "dev" or "prod" (for filtering in presentations)
    """
    
    logger.info("="*60)
    logger.info("GENERATE CONSPIRACY + PUSH DOCUMENTS")
    logger.info("="*60)
    logger.info(f"Environment: {environment.upper()}")
    logger.info("")
    
    # Check keys
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    arkiv_key = os.getenv("ARKIV_PRIVATE_KEY")
    
    if not cerebras_key:
        logger.error("❌ CEREBRAS_API_KEY required")
        return
    
    # Step 1: Generate conspiracy
    logger.info("🎲 Generating conspiracy...")
    logger.info("")
    
    llm = CerebrasClient(cerebras_key)
    config = {
        "political_context": {"temperature": 0.8, "max_tokens": 4000},
        "conspiracy": {"temperature": 0.8, "max_tokens": 1500},
        "psychological": {"temperature": 0.7, "max_tokens": 2000},
        "cryptographic": {"temperature": 0.7, "max_tokens": 1500},
        "document_generation": {"temperature": 0.7, "max_tokens": 4000, "parallel_batch_size": 5},
        "character_enhancement": {"temperature": 0.7, "max_tokens": 1500},
        "num_images": 2
    }
    
    pipeline = ConspiracyPipeline(llm, config, replicate_token=os.getenv("REPLICATE_API_TOKEN"))
    
    try:
        mystery = await pipeline.generate_conspiracy_mystery(
            difficulty=6,
            num_documents=20,
            conspiracy_type="occult"
        )
        
        logger.info("")
        logger.info(f"✅ Generated: {mystery.premise.conspiracy_name}")
        logger.info(f"   Documents: {len(mystery.documents)}")
        logger.info(f"   Mystery ID: {mystery.mystery_id}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return
    
    # Step 2: Push to Arkiv (if key available)
    if not arkiv_key:
        logger.info("⏭️  No ARKIV_PRIVATE_KEY - skipping upload")
        return
    
    logger.info("📤 Pushing to Arkiv...")
    logger.info("")
    
    try:
        async with ArkivClient(
            private_key=arkiv_key,
            rpc_url=os.getenv("ARKIV_RPC_URL", "https://kaolin.hoodi.arkiv.network/rpc"),
            ws_url=os.getenv("ARKIV_WS_URL", "wss://kaolin.hoodi.arkiv.network/rpc/ws")
        ) as client:
            
            # Build entities for documents
            entities = []
            
            # 1. Metadata entity (with semantic attributes)
            metadata = {
                "mystery_id": mystery.mystery_id,
                "conspiracy_name": mystery.premise.conspiracy_name,
                "world": mystery.political_context.world_name,
                "difficulty": mystery.difficulty,
                "total_documents": len(mystery.documents),
                "created_at": mystery.created_at
            }
            
            entities.append({
                "payload": json.dumps(metadata).encode('utf-8'),
                "content_type": "application/json",
                "attributes": {
                    # ✅ SEMANTIC ATTRIBUTES (meaningful, filterable)
                    "resource_type": "conspiracy",  # Clear purpose!
                    "mystery_id": mystery.mystery_id,
                    "world": mystery.political_context.world_name,
                    "difficulty": str(mystery.difficulty),
                    "conspiracy_type": mystery.premise.conspiracy_type,  # From mystery data!
                    "environment": environment,  # dev or prod
                    "status": "active"
                },
                "expires_in": 604800  # 7 days
            })
            
            # 2. Document entities (with semantic attributes)
            for doc in mystery.documents:
                doc_data = {
                    "document_id": doc.get("document_id"),
                    "document_type": doc.get("document_type"),
                    "fields": doc.get("fields", {})
                }
                
                entities.append({
                    "payload": json.dumps(doc_data).encode('utf-8'),
                    "content_type": "application/json",
                    "attributes": {
                        # ✅ SEMANTIC ATTRIBUTES (meaningful, filterable)
                        "resource_type": "document",  # Clear purpose!
                        "mystery_id": mystery.mystery_id,
                        "document_id": doc.get("document_id"),
                        "doc_type": doc.get("document_type"),  # Filterable by type!
                        "world": mystery.political_context.world_name,
                        "environment": environment  # dev or prod
                    },
                    "expires_in": 604800
                })
            
            # Push in batches
            batch_size = 10
            total_pushed = 0
            
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i+batch_size]
                keys = await client.create_entities_batch(batch)
                total_pushed += len(keys)
                logger.info(f"   ✅ Batch {i//batch_size + 1}: {len(keys)} entities")
            
            logger.info("")
            logger.info(f"✅ Pushed {total_pushed} entities to Arkiv")
            logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Arkiv push failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    logger.info("="*60)
    logger.info("🎉 COMPLETE")
    logger.info("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate and push conspiracy to Arkiv')
    parser.add_argument(
        '--env',
        choices=['dev', 'prod'],
        default='dev',
        help='Environment tag (dev or prod) for filtering'
    )
    
    args = parser.parse_args()
    
    asyncio.run(generate_and_push(environment=args.env))

