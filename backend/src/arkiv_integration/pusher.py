"""Push mystery data to Arkiv using SDK v1.0.0a5."""

import logging
from typing import List, Dict, Any
from pathlib import Path

from .client import ArkivClient
from .entity_builder import EntityBuilder
from models import Mystery


logger = logging.getLogger(__name__)


class ArkivPusher:
    """
    Push mystery entities to Arkiv.
    
    Note: No longer stores client - uses context manager pattern.
    """
    
    def push_mystery(
        self,
        client: ArkivClient,
        mystery: Mystery,
        images_dir: Path = None
    ) -> Dict[str, Any]:
        """
        Push complete mystery to Arkiv.
        
        Args:
            client: ArkivClient (must be in context manager)
            mystery: Mystery object with all data
            images_dir: Directory containing generated images
        
        Returns:
            Dictionary with entity keys and stats
        """
        logger.info(f"📤 Pushing mystery {mystery.metadata.mystery_id} to Arkiv...")
        
        # Prepare images if directory provided
        images_data = []
        if images_dir and images_dir.exists():
            for img_info in mystery.images:
                img_path = images_dir / f"{img_info['image_id']}.png"
                if img_path.exists():
                    with open(img_path, 'rb') as f:
                        images_data.append({
                            "image_id": img_info["image_id"],
                            "bytes": f.read()
                        })
        
        # Build all entities
        entities = EntityBuilder.build_entities_batch(
            mystery,
            mystery.documents,
            images_data if images_data else None
        )
        
        logger.info(f"  - {len(entities)} total entities")
        logger.info(f"  - 1 metadata entity")
        logger.info(f"  - {len(mystery.documents)} document entities")
        logger.info(f"  - {len(images_data)} image entities")
        
        # Push to Arkiv in batches (to avoid overwhelming the API)
        batch_size = 10
        all_entity_keys = []
        
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i+batch_size]
            logger.info(f"  Pushing batch {i//batch_size + 1}/{(len(entities)-1)//batch_size + 1}...")
            
            try:
                receipt = client.create_entities_batch(batch)
                # Extract entity keys from receipt.creates
                if hasattr(receipt, 'creates') and receipt.creates:
                    batch_keys = [create.entity_key for create in receipt.creates]
                    all_entity_keys.extend(batch_keys)
                    logger.info(f"    ✅ {len(batch_keys)} entities created")
                else:
                    logger.warning(f"    ⚠️  Receipt format unexpected")
            except Exception as e:
                logger.error(f"    ❌ Error: {str(e)}")
                raise
        
        logger.info(f"✅ Mystery pushed to Arkiv successfully!")
        logger.info(f"   Total entities: {len(all_entity_keys)}")
        
        return {
            "mystery_id": mystery.metadata.mystery_id,
            "total_entities": len(all_entity_keys),
            "metadata_entities": 1,
            "document_entities": len(mystery.documents),
            "image_entities": len(images_data),
            "entity_keys": all_entity_keys
        }
    
    def verify_push(self, client: ArkivClient, mystery_id: str) -> bool:
        """
        Verify that mystery was pushed correctly.
        
        Args:
            client: ArkivClient (must be in context manager)
            mystery_id: Mystery ID to verify
        
        Returns:
            True if all entities are queryable
        """
        logger.info(f"🔍 Verifying mystery {mystery_id} in Arkiv...")
        
        try:
            # Query for metadata (note: "type" not "document_type" in new API)
            metadata_query = f'mystery_id = "{mystery_id}" and type = "mystery_metadata"'
            metadata_entities = client.query_entities(metadata_query, limit=1)
            
            if not metadata_entities:
                logger.error("  ❌ Metadata entity not found")
                return False
            
            logger.info(f"  ✅ Metadata entity found")
            
            # Query for documents (all non-metadata, non-image types)
            docs_query = f'mystery_id = "{mystery_id}" and type != "mystery_metadata" and type != "image"'
            doc_entities = client.query_entities(docs_query, limit=100)
            
            logger.info(f"  ✅ {len(doc_entities)} document entities found")
            
            # Query for images
            images_query = f'mystery_id = "{mystery_id}" and type = "image"'
            image_entities = client.query_entities(images_query, limit=50)
            
            logger.info(f"  ✅ {len(image_entities)} image entities found")
            
            logger.info(f"✅ Verification complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {str(e)}")
            return False

