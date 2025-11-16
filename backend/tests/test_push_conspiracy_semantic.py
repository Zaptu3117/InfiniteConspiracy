"""Generate conspiracy and push with SEMANTIC attributes to Arkiv."""

import asyncio
import logging
import sys
import os
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from narrative.conspiracy import ConspiracyPipeline
from utils import CerebrasClient
from arkiv_integration import ArkivClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def generate_and_push():
    """Generate conspiracy and push with semantic, queryable attributes."""
    
    logger.info("="*60)
    logger.info("GENERATE + PUSH WITH SEMANTIC ATTRIBUTES")
    logger.info("="*60)
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
    
    # Step 2: Push to Arkiv with SEMANTIC attributes
    if not arkiv_key:
        logger.info("⏭️  No ARKIV_PRIVATE_KEY - skipping upload")
        return
    
    logger.info("📤 Pushing to Arkiv with semantic attributes...")
    logger.info("")
    
    try:
        async with ArkivClient(
            private_key=arkiv_key,
            rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
            ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
        ) as client:
            
            # Build entities with SEMANTIC attributes
            entities = []
            
            # ========================================
            # 1. CONSPIRACY METADATA (Discoverable!)
            # ========================================
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
                    # ✅ SEMANTIC ATTRIBUTES (Meaningful & Queryable)
                    "resource_type": "conspiracy",  # Clear purpose!
                    "mystery_id": mystery.mystery_id,
                    "world": mystery.political_context.world_name,  # Filter by world
                    "difficulty": str(mystery.difficulty),  # Filter by difficulty
                    "conspiracy_type": "occult",  # Filter by theme
                    "status": "active",  # Filter by state
                    "total_docs": str(len(mystery.documents))  # Quick stats
                },
                "expires_in": 604800  # 7 days
            })
            
            logger.info("   Metadata attributes:")
            logger.info("      ✅ resource_type = 'conspiracy' (semantic!)")
            logger.info("      ✅ world (filterable)")
            logger.info("      ✅ difficulty (filterable)")
            logger.info("      ✅ conspiracy_type (filterable)")
            logger.info("      ✅ status (filterable)")
            logger.info("")
            
            # ========================================
            # 2. DOCUMENTS (Filterable by type!)
            # ========================================
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
                        # ✅ SEMANTIC ATTRIBUTES
                        "resource_type": "document",  # Clear purpose!
                        "mystery_id": mystery.mystery_id,
                        "document_id": doc.get("document_id"),
                        "doc_type": doc.get("document_type"),  # Filter by type (email, log, etc.)
                        "world": mystery.political_context.world_name  # Same world as mystery
                    },
                    "expires_in": 604800
                })
            
            logger.info(f"   Document attributes (x{len(mystery.documents)}):")
            logger.info("      ✅ resource_type = 'document' (semantic!)")
            logger.info("      ✅ doc_type = 'email' | 'network_log' | etc. (filterable!)")
            logger.info("      ✅ world (same as mystery)")
            logger.info("")
            
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
            
            # ========================================
            # 3. SHOW NEW QUERY EXAMPLES
            # ========================================
            logger.info("="*60)
            logger.info("✨ NEW SEMANTIC QUERIES")
            logger.info("="*60)
            logger.info("")
            logger.info("// Discover all conspiracies")
            logger.info('query.where(eq("resource_type", "conspiracy"))')
            logger.info("")
            logger.info("// Filter by world")
            logger.info(f'query.where(eq("world", "{mystery.political_context.world_name}"))')
            logger.info("")
            logger.info("// Filter by difficulty")
            logger.info('query.where(eq("difficulty", "6"))')
            logger.info("")
            logger.info("// Get all emails for a mystery")
            logger.info('query.where(eq("mystery_id", "..."))')
            logger.info('     .where(eq("doc_type", "email"))')
            logger.info("")
            logger.info("// Get all documents in a world")
            logger.info(f'query.where(eq("world", "{mystery.political_context.world_name}"))')
            logger.info('     .where(eq("resource_type", "document"))')
            logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Arkiv push failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    logger.info("="*60)
    logger.info("🎉 COMPLETE WITH SEMANTIC ATTRIBUTES")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(generate_and_push())

