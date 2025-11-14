"""Document data models."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid


class DocumentField(BaseModel):
    """A single field in a document."""
    
    name: str
    value: Any
    encrypted: bool = False


class Document(BaseModel):
    """Structured document model."""
    
    document_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    document_type: str
    fields: Dict[str, Any] = Field(default_factory=dict)
    
    # Encryption info
    cipher_info: Optional[Dict[str, Any]] = None
    
    # Metadata (not included in Arkiv annotations)
    contains_clues: List[str] = Field(default_factory=list)
    proof_step: Optional[int] = None
    
    def to_arkiv_format(self) -> Dict[str, Any]:
        """
        Format document for Arkiv storage.
        Only includes document_id, document_type, and fields.
        NO SPOILERS in the structure!
        """
        result = {
            "document_id": self.document_id,
            "document_type": self.document_type,
            "fields": self.fields
        }
        
        # Only include cipher_info if document is encrypted
        if self.cipher_info:
            result["cipher_info"] = self.cipher_info
        
        return result
    
    def get_annotations(self, mystery_id: str) -> Dict[str, List]:
        """
        Get Arkiv annotations for this document.
        CRITICAL: Only include non-spoiler annotations!
        """
        import time
        
        return {
            "string": [
                {"key": "mystery_id", "value": mystery_id},
                {"key": "document_type", "value": self.document_type},
                {"key": "document_id", "value": self.document_id}
            ],
            "numeric": [
                {"key": "created_at", "value": int(time.time())}
            ]
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return self.dict()

