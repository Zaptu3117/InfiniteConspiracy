"""Query conspiracy mystery from Arkiv."""

import asyncio
import logging
import sys
import os
import json

# Load .env file
from dotenv import load_dotenv
load_dotenv()

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from arkiv_integration import ArkivClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def query_mystery_from_arkiv(mystery_id: str = None):
    """Query and display mystery from Arkiv."""
    
    logger.info("="*60)
    logger.info("QUERY CONSPIRACY FROM ARKIV")
    logger.info("="*60)
    logger.info("")
    
    # Check key
    arkiv_key = os.getenv("ARKIV_PRIVATE_KEY")
    if not arkiv_key:
        logger.error("❌ ARKIV_PRIVATE_KEY required")
        return
    
    # If no mystery_id provided, use the latest from local
    if not mystery_id:
        from pathlib import Path
        conspiracies_dir = Path("outputs/conspiracies")
        mystery_dirs = sorted([d for d in conspiracies_dir.iterdir() if d.is_dir()],
                             key=lambda x: x.stat().st_mtime, reverse=True)
        
        if mystery_dirs:
            mystery_file = mystery_dirs[0] / "mystery.json"
            with open(mystery_file) as f:
                data = json.load(f)
                mystery_id = data['mystery_id']
                logger.info(f"📂 Using latest local mystery: {mystery_dirs[0].name}")
        else:
            logger.error("❌ No mystery_id provided and no local mysteries found")
            return
    
    logger.info(f"🔍 Querying mystery: {mystery_id}")
    logger.info("")
    
    try:
        async with ArkivClient(
            private_key=arkiv_key,
            rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
            ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
        ) as client:
            
            # Query all entities for this mystery
            query_string = f'mystery_id = "{mystery_id}"'
            logger.info(f"   Query: {query_string}")
            logger.info("")
            
            entities = await client.query_entities(query_string, limit=100)
            
            if not entities:
                logger.warning(f"❌ No entities found for mystery {mystery_id}")
                return
            
            logger.info(f"✅ Found {len(entities)} entities")
            logger.info("")
            
            # Separate by entity type
            metadata_entities = []
            document_entities = []
            image_entities = []
            
            for entity in entities:
                resource_type = entity.attributes.get("resource_type", "unknown")
                
                if resource_type == "conspiracy":
                    metadata_entities.append(entity)
                elif resource_type == "document":
                    document_entities.append(entity)
                elif resource_type == "image":
                    image_entities.append(entity)
            
            logger.info("="*60)
            logger.info("ENTITY BREAKDOWN")
            logger.info("="*60)
            logger.info(f"Metadata: {len(metadata_entities)}")
            logger.info(f"Documents: {len(document_entities)}")
            logger.info(f"Images: {len(image_entities)}")
            logger.info("")
            
            # Display metadata
            if metadata_entities:
                logger.info("="*60)
                logger.info("METADATA")
                logger.info("="*60)
                
                for meta in metadata_entities:
                    data = json.loads(meta.payload.decode('utf-8'))
                    logger.info(f"Conspiracy: {data.get('conspiracy_name')}")
                    logger.info(f"World: {data.get('world')}")
                    logger.info(f"Difficulty: {data.get('difficulty')}/10")
                    logger.info(f"Total Documents: {data.get('total_documents')}")
                    logger.info(f"Created: {data.get('created_at')}")
                    logger.info("")
            
            # Display sample documents
            if document_entities:
                logger.info("="*60)
                logger.info("SAMPLE DOCUMENTS (first 3)")
                logger.info("="*60)
                
                for i, doc_entity in enumerate(document_entities[:3], 1):
                    doc_data = json.loads(doc_entity.payload.decode('utf-8'))
                    
                    logger.info(f"\n{i}. {doc_data.get('document_id')}")
                    logger.info(f"   Type: {doc_data.get('document_type')}")
                    logger.info(f"   Fields: {list(doc_data.get('fields', {}).keys())}")
                    
                    # Show a sample field
                    fields = doc_data.get('fields', {})
                    if fields:
                        first_field = list(fields.keys())[0]
                        value = fields[first_field]
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        logger.info(f"   {first_field}: {value}")
                
                logger.info("")
                if len(document_entities) > 3:
                    logger.info(f"   ... and {len(document_entities) - 3} more documents")
                logger.info("")
            
            # Display images
            if image_entities:
                logger.info("="*60)
                logger.info("IMAGES")
                logger.info("="*60)
                
                for img_entity in image_entities:
                    img_size = len(img_entity.payload)
                    img_id = img_entity.attributes.get("document_id", "unknown")
                    logger.info(f"   {img_id}: {img_size:,} bytes")
                
                logger.info("")
            
            logger.info("="*60)
            logger.info("✅ QUERY COMPLETE")
            logger.info("="*60)
            logger.info("")
            logger.info("Query results:")
            logger.info(f"  - Mystery ID: {mystery_id}")
            logger.info(f"  - Total entities: {len(entities)}")
            logger.info(f"  - Documents: {len(document_entities)}")
            logger.info(f"  - Images: {len(image_entities)}")
            logger.info("")
            logger.info("Frontend can query with:")
            logger.info(f'  query: mystery_id = "{mystery_id}"')
            logger.info(f'  or: mystery_id = "{mystery_id}" and entity_type = "document"')
            logger.info("")
    
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    # Allow passing mystery_id as argument
    mystery_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    asyncio.run(query_mystery_from_arkiv(mystery_id))

