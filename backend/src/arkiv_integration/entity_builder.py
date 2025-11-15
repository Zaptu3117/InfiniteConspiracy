"""Build Arkiv entities from mystery data for SDK v1.0.0a5."""

import json
from typing import Dict, Any, List
from models import Mystery


class EntityBuilder:
    """
    Build Arkiv entities with proper format for SDK v1.0.0a5.
    
    Key changes from old API:
    - Uses 'payload', 'content_type', 'attributes', 'btl'
    - No more separate string_annotations/numeric_annotations
    - All attributes go in single dict
    """
    
    @staticmethod
    def build_mystery_metadata_entity(mystery: Mystery) -> Dict[str, Any]:
        """
        Build mystery metadata entity.
        
        Returns entity spec ready for create_entity or batch creation.
        """
        metadata = mystery.to_arkiv_metadata()
        
        # Calculate BTL from expires_in (seconds to blocks, ~12s per block)
        btl = mystery.metadata.expires_in // 12
        
        return {
            "payload": json.dumps(metadata).encode('utf-8'),
            "content_type": "application/json",
            "attributes": {
                "mystery_id": mystery.metadata.mystery_id,
                "type": "mystery_metadata",
                "difficulty": mystery.metadata.difficulty,
                "created_at": mystery.metadata.created_at
            },
            "btl": btl
        }
    
    @staticmethod
    def build_document_entity(
        document: Dict[str, Any],
        mystery_id: str,
        btl: int = 7200  # ~7 days in blocks
    ) -> Dict[str, Any]:
        """
        Build document entity.
        
        CRITICAL: Only include non-spoiler attributes!
        No proof steps, no clue indicators, just basic metadata.
        """
        # Extract document data (remove internal metadata)
        doc_data = {
            "document_id": document["document_id"],
            "document_type": document["document_type"],
            "fields": document["fields"]
        }
        
        # Include cipher_info if present
        if "cipher_info" in document and document["cipher_info"]:
            doc_data["cipher_info"] = document["cipher_info"]
        
        return {
            "payload": json.dumps(doc_data).encode('utf-8'),
            "content_type": "application/json",
            "attributes": {
                "mystery_id": mystery_id,
                "type": document["document_type"],
                "document_id": document["document_id"],
                "created_at": document.get("created_at", 0)
            },
            "btl": btl
        }
    
    @staticmethod
    def build_image_entity(
        image_bytes: bytes,
        mystery_id: str,
        image_id: str,
        btl: int = 7200
    ) -> Dict[str, Any]:
        """
        Build image entity.
        
        NO SPOILERS - just image bytes and basic metadata!
        Uses image/png content type.
        """
        return {
            "payload": image_bytes,
            "content_type": "image/png",
            "attributes": {
                "mystery_id": mystery_id,
                "type": "image",
                "document_id": image_id
            },
            "btl": btl
        }
    
    @staticmethod
    def build_entities_batch(
        mystery: Mystery,
        documents: List[Dict[str, Any]],
        images: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Build all entities for a mystery.
        
        Returns list of entity specs ready for batch creation.
        """
        entities = []
        
        # Calculate BTL from expires_in (seconds to blocks)
        btl = mystery.metadata.expires_in // 12
        
        # Mystery metadata
        entities.append(EntityBuilder.build_mystery_metadata_entity(mystery))
        
        # Documents
        for doc in documents:
            entities.append(EntityBuilder.build_document_entity(
                doc,
                mystery.metadata.mystery_id,
                btl
            ))
        
        # Images
        if images:
            for img in images:
                entities.append(EntityBuilder.build_image_entity(
                    img["bytes"],
                    mystery.metadata.mystery_id,
                    img["image_id"],
                    btl
                ))
        
        return entities

