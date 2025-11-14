"""Mystery data models."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import uuid


class MysteryMetadata(BaseModel):
    """Metadata for a mystery."""
    
    mystery_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    difficulty: int = Field(ge=1, le=10)
    total_documents: int
    total_images: int
    created_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    expires_in: int = 604800  # 7 days in seconds


class Mystery(BaseModel):
    """Complete mystery data structure."""
    
    metadata: MysteryMetadata
    answer: str
    answer_hash: str = ""
    
    # Proof tree
    proof_tree: Dict[str, Any]
    proof_hash: str = ""
    
    # Generated content
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    images: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Validation results
    validation_passed: bool = False
    validation_details: Dict[str, Any] = Field(default_factory=dict)
    
    def generate_hashes(self):
        """Generate answer and proof hashes."""
        # Answer hash (lowercase, stripped)
        answer_normalized = self.answer.lower().strip()
        self.answer_hash = "0x" + hashlib.sha256(
            answer_normalized.encode('utf-8')
        ).hexdigest()
        
        # Proof hash (from proof tree JSON)
        import json
        proof_json = json.dumps(self.proof_tree, sort_keys=True)
        self.proof_hash = "0x" + hashlib.sha256(
            proof_json.encode('utf-8')
        ).hexdigest()
    
    def to_blockchain_format(self) -> Dict[str, Any]:
        """Format for blockchain registration."""
        return {
            "mystery_id": "0x" + hashlib.sha256(
                self.metadata.mystery_id.encode('utf-8')
            ).hexdigest(),
            "answer_hash": self.answer_hash,
            "proof_hash": self.proof_hash,
            "difficulty": self.metadata.difficulty,
            "duration": self.metadata.expires_in
        }
    
    def to_arkiv_metadata(self) -> Dict[str, Any]:
        """Format mystery metadata for Arkiv."""
        return {
            "mystery_id": self.metadata.mystery_id,
            "question": self.metadata.question,
            "difficulty": self.metadata.difficulty,
            "total_documents": self.metadata.total_documents,
            "total_images": self.metadata.total_images,
            "created_at": self.metadata.created_at
        }
    
    def save_to_file(self, output_dir: str):
        """Save mystery to JSON file."""
        import json
        from pathlib import Path
        
        output_path = Path(output_dir) / self.metadata.mystery_id
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save complete mystery
        with open(output_path / "mystery.json", 'w') as f:
            json.dump(self.dict(), f, indent=2)
        
        # Save proof tree separately
        with open(output_path / "proof_tree.json", 'w') as f:
            json.dump(self.proof_tree, f, indent=2)
        
        # Save documents
        docs_dir = output_path / "documents"
        docs_dir.mkdir(exist_ok=True)
        for doc in self.documents:
            doc_file = docs_dir / f"{doc['document_id']}.json"
            with open(doc_file, 'w') as f:
                json.dump(doc, f, indent=2)
        
        # Create images directory
        images_dir = output_path / "images"
        images_dir.mkdir(exist_ok=True)
        
        return output_path

