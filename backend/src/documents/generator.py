"""Document generator for structured JSON documents."""

import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Generate structured JSON documents."""
    
    def __init__(self):
        """Initialize document generator."""
        pass
    
    def generate_document(
        self,
        document_type: str,
        document_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a document from template.
        
        Args:
            document_type: Type of document (email, diary, etc.)
            document_id: Unique document identifier
            fields: Field values for the template
        
        Returns:
            Document dict ready for Arkiv
        """
        logger.debug(f"Generating {document_type} document: {document_id}")
        
        # Create document structure
        document = {
            "document_id": document_id,
            "document_type": document_type,
            "fields": fields
        }
        
        return document
    
    def generate_batch(
        self,
        specs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple documents.
        
        Args:
            specs: List of document specifications
        
        Returns:
            List of generated documents
        """
        documents = []
        
        for spec in specs:
            doc = self.generate_document(
                spec["document_type"],
                spec["document_id"],
                spec["fields"]
            )
            
            # Add cipher info if present
            if "cipher_info" in spec:
                doc["cipher_info"] = spec["cipher_info"]
            
            documents.append(doc)
        
        logger.info(f"Generated {len(documents)} documents")
        return documents

