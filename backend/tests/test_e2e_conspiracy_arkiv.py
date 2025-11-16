"""
End-to-End Test: Generate → Deploy → Fetch
Full pipeline test for conspiracy mysteries on Arkiv
"""

import asyncio
import logging
import sys
import os
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from narrative.conspiracy import ConspiracyPipeline
from utils import CerebrasClient
from arkiv_integration import ArkivClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def e2e_test(
    environment: str = "dev",  # "dev" or "prod"
    difficulty: int = 6,
    num_documents: int = 20,
    conspiracy_type: str = "occult"
):
    """
    Complete E2E test: Generate → Deploy → Fetch
    
    Args:
        environment: "dev" or "prod" (for filtering in presentations)
        difficulty: Mystery difficulty (1-10)
        num_documents: Number of documents to generate
        conspiracy_type: "occult", "secret_society", or "underground_network"
    """
    
    logger.info("="*60)
    logger.info("🚀 END-TO-END CONSPIRACY PIPELINE TEST")
    logger.info("="*60)
    logger.info("")
    logger.info(f"Environment: {environment.upper()}")
    logger.info(f"Difficulty: {difficulty}/10")
    logger.info(f"Documents: {num_documents}")
    logger.info(f"Type: {conspiracy_type}")
    logger.info("")
    
    # Validate environment
    if environment not in ["dev", "prod"]:
        logger.error("❌ Environment must be 'dev' or 'prod'")
        return None
    
    # Check API keys
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    arkiv_key = os.getenv("ARKIV_PRIVATE_KEY")
    
    if not cerebras_key:
        logger.error("❌ CEREBRAS_API_KEY required")
        return None
    
    if not arkiv_key:
        logger.error("❌ ARKIV_PRIVATE_KEY required")
        logger.info("   (Skipping Arkiv upload)")
        upload_to_arkiv = False
    else:
        upload_to_arkiv = True
    
    # ========================================
    # STEP 1: GENERATE CONSPIRACY
    # ========================================
    logger.info("="*60)
    logger.info("STEP 1: GENERATING CONSPIRACY")
    logger.info("="*60)
    logger.info("")
    
    llm = CerebrasClient(cerebras_key)
    config = {
        "political_context": {"temperature": 0.8, "max_tokens": 8000},
        "conspiracy": {"temperature": 0.8, "max_tokens": 8000},
        "psychological": {"temperature": 0.7, "max_tokens": 8000},
        "cryptographic": {"temperature": 0.7, "max_tokens": 8000},
        "document_generation": {"temperature": 0.7, "max_tokens": 8000, "parallel_batch_size": 5},
        "character_enhancement": {"temperature": 0.7, "max_tokens": 8000},
        "num_images": 2
    }
    
    pipeline = ConspiracyPipeline(llm, config, replicate_token=os.getenv("REPLICATE_API_TOKEN"))
    
    try:
        start_time = datetime.now()
        
        mystery = await pipeline.generate_conspiracy_mystery(
            difficulty=difficulty,
            num_documents=num_documents,
            conspiracy_type=conspiracy_type
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        logger.info("")
        logger.info("✅ GENERATION COMPLETE")
        logger.info(f"   Time: {generation_time:.1f}s")
        logger.info(f"   Mystery: {mystery.premise.conspiracy_name}")
        logger.info(f"   World: {mystery.political_context.world_name}")
        logger.info(f"   Documents: {len(mystery.documents)}")
        logger.info(f"   Sub-graphs: {len(mystery.subgraphs)}")
        logger.info(f"   Characters: {len(mystery.characters)}")
        logger.info(f"   Crypto keys: {len(mystery.crypto_keys)}")
        logger.info(f"   Mystery ID: {mystery.mystery_id}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    if not upload_to_arkiv:
        logger.info("⏭️  Skipping Arkiv steps (no API key)")
        return {
            "mystery_id": mystery.mystery_id,
            "conspiracy_name": mystery.premise.conspiracy_name,
            "documents": len(mystery.documents),
            "uploaded": False
        }
    
    # ========================================
    # STEP 2: DEPLOY TO ARKIV
    # ========================================
    logger.info("="*60)
    logger.info("STEP 2: DEPLOYING TO ARKIV")
    logger.info("="*60)
    logger.info("")
    
    try:
        async with ArkivClient(
            private_key=arkiv_key,
            rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
            ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
        ) as client:
            
            entities = []
            
            # 1. CONSPIRACY METADATA (with environment tag)
            metadata = {
                "mystery_id": mystery.mystery_id,
                "conspiracy_name": mystery.premise.conspiracy_name,
                "world": mystery.political_context.world_name,
                "difficulty": mystery.difficulty,
                "total_documents": len(mystery.documents),
                "created_at": mystery.created_at,
                "environment": environment  # Store in payload too
            }
            
            entities.append({
                "payload": json.dumps(metadata).encode('utf-8'),
                "content_type": "application/json",
                "attributes": {
                    # SEMANTIC ATTRIBUTES
                    "resource_type": "conspiracy",
                    "mystery_id": mystery.mystery_id,
                    "world": mystery.political_context.world_name,
                    "difficulty": str(mystery.difficulty),
                    "conspiracy_type": mystery.premise.conspiracy_type,
                    "environment": environment,  # ✅ DEV or PROD TAG!
                    "status": "active"
                },
                "expires_in": 604800  # 7 days
            })
            
            logger.info(f"   Metadata attributes:")
            logger.info(f"      resource_type: conspiracy")
            logger.info(f"      world: {mystery.political_context.world_name}")
            logger.info(f"      difficulty: {mystery.difficulty}")
            logger.info(f"      conspiracy_type: {mystery.premise.conspiracy_type}")
            logger.info(f"      environment: {environment} ← FILTERABLE!")
            logger.info(f"      status: active")
            logger.info("")
            
            # 2. DOCUMENTS
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
                        "resource_type": "document",
                        "mystery_id": mystery.mystery_id,
                        "document_id": doc.get("document_id"),
                        "doc_type": doc.get("document_type"),
                        "world": mystery.political_context.world_name,
                        "environment": environment  # ✅ Same tag on documents
                    },
                    "expires_in": 604800
                })
            
            # Push in batches
            logger.info(f"   Pushing {len(entities)} entities...")
            batch_size = 10
            total_pushed = 0
            
            upload_start = datetime.now()
            
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i+batch_size]
                keys = await client.create_entities_batch(batch)
                total_pushed += len(keys)
                logger.info(f"      Batch {i//batch_size + 1}: {len(keys)} entities")
            
            upload_time = (datetime.now() - upload_start).total_seconds()
            
            logger.info("")
            logger.info("✅ DEPLOYMENT COMPLETE")
            logger.info(f"   Time: {upload_time:.1f}s")
            logger.info(f"   Total entities: {total_pushed}")
            logger.info(f"   - 1 conspiracy metadata")
            logger.info(f"   - {len(mystery.documents)} documents")
            logger.info("")
    
    except Exception as e:
        logger.error(f"❌ Arkiv deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 3: FETCH FROM ARKIV (Verification)
    # ========================================
    logger.info("="*60)
    logger.info("STEP 3: FETCHING FROM ARKIV (Verification)")
    logger.info("="*60)
    logger.info("")
    
    try:
        async with ArkivClient(
            private_key=arkiv_key,
            rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
            ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
        ) as client:
            
            # Query 1: Get this specific mystery
            logger.info(f"   Query 1: Fetching mystery {mystery.mystery_id[:16]}...")
            query_string = f'mystery_id = "{mystery.mystery_id}"'
            entities = await client.query_entities(query_string, limit=100)
            
            logger.info(f"   ✅ Found {len(entities)} entities")
            
            # Separate by type
            conspiracy = [e for e in entities if e.attributes.get("resource_type") == "conspiracy"]
            documents = [e for e in entities if e.attributes.get("resource_type") == "document"]
            
            logger.info(f"      - 1 conspiracy metadata")
            logger.info(f"      - {len(documents)} documents")
            logger.info("")
            
            # Query 2: Get all conspiracies in this environment
            logger.info(f"   Query 2: All {environment} conspiracies...")
            query_string = f'environment = "{environment}"'
            env_entities = await client.query_entities(query_string, limit=100)
            
            env_conspiracies = [e for e in env_entities if e.attributes.get("resource_type") == "conspiracy"]
            logger.info(f"   ✅ Found {len(env_conspiracies)} {environment} conspiracies total")
            
            for i, entity in enumerate(env_conspiracies, 1):
                data = json.loads(entity.payload.decode('utf-8'))
                logger.info(f"      {i}. {data['conspiracy_name']} (diff: {data['difficulty']})")
            
            logger.info("")
            
            # Query 3: Verify attributes
            if conspiracy:
                logger.info("   Query 3: Verifying attributes...")
                c = conspiracy[0]
                logger.info(f"   ✅ Attributes verified:")
                logger.info(f"      resource_type: {c.attributes.get('resource_type')}")
                logger.info(f"      environment: {c.attributes.get('environment')} ✓")
                logger.info(f"      world: {c.attributes.get('world')}")
                logger.info(f"      difficulty: {c.attributes.get('difficulty')}")
                logger.info(f"      conspiracy_type: {c.attributes.get('conspiracy_type')}")
                logger.info("")
    
    except Exception as e:
        logger.error(f"❌ Fetch verification failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    logger.info("="*60)
    logger.info("✅ E2E TEST COMPLETE")
    logger.info("="*60)
    logger.info("")
    logger.info("Summary:")
    logger.info(f"  Mystery: {mystery.premise.conspiracy_name}")
    logger.info(f"  Mystery ID: {mystery.mystery_id}")
    logger.info(f"  Environment: {environment}")
    logger.info(f"  World: {mystery.political_context.world_name}")
    logger.info(f"  Difficulty: {mystery.difficulty}/10")
    logger.info(f"  Type: {mystery.premise.conspiracy_type}")
    logger.info(f"  Documents: {len(mystery.documents)}")
    logger.info(f"  Generation time: {generation_time:.1f}s")
    logger.info(f"  Upload time: {upload_time:.1f}s")
    logger.info("")
    logger.info("Frontend Queries:")
    logger.info(f'  // Get all {environment} conspiracies')
    logger.info(f'  query.where(eq("environment", "{environment}"))')
    logger.info("")
    logger.info(f'  // Get this specific mystery')
    logger.info(f'  query.where(eq("mystery_id", "{mystery.mystery_id}"))')
    logger.info("")
    logger.info(f'  // Get {environment} conspiracies in this world')
    logger.info(f'  query.where(eq("environment", "{environment}"))')
    logger.info(f'       .where(eq("world", "{mystery.political_context.world_name}"))')
    logger.info("")
    
    return {
        "mystery_id": mystery.mystery_id,
        "conspiracy_name": mystery.premise.conspiracy_name,
        "environment": environment,
        "world": mystery.political_context.world_name,
        "difficulty": mystery.difficulty,
        "conspiracy_type": mystery.premise.conspiracy_type,
        "documents": len(mystery.documents),
        "generation_time": generation_time,
        "upload_time": upload_time,
        "uploaded": True
    }


async def main():
    """Run E2E test with command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description='E2E Conspiracy Pipeline Test')
    parser.add_argument(
        '--env',
        choices=['dev', 'prod'],
        default='dev',
        help='Environment tag (dev or prod)'
    )
    parser.add_argument(
        '--difficulty',
        type=int,
        default=6,
        choices=range(1, 11),
        help='Mystery difficulty (1-10)'
    )
    parser.add_argument(
        '--docs',
        type=int,
        default=20,
        help='Number of documents'
    )
    parser.add_argument(
        '--type',
        type=str,
        default='occult',
        help='Conspiracy type (any narrative seed: reptilians, flat_earth, templar, occult, etc.)'
    )
    
    args = parser.parse_args()
    
    result = await e2e_test(
        environment=args.env,
        difficulty=args.difficulty,
        num_documents=args.docs,
        conspiracy_type=args.type
    )
    
    if result:
        logger.info("🎉 E2E test passed!")
        return 0
    else:
        logger.error("❌ E2E test failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)



