"""Red Herring Generator - add subtle false leads to mysteries."""

import logging
import random
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class RedHerringGenerator:
    """
    Generate subtle red herrings (false leads) for mysteries.
    
    Strategy:
    - Add 2-3 misleading but plausible details
    - Keep them subtle - don't make mystery unsolvable
    - Insert into random documents
    - Mix truth with misdirection
    """
    
    def __init__(self):
        self.red_herring_types = [
            "suspicious_timing",
            "false_alibi",
            "misleading_reference",
            "red_herring_character",
            "coincidental_evidence"
        ]
    
    def add_red_herrings(
        self,
        documents: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Add red herrings to documents.
        
        Args:
            documents: List of generated documents
            config: Red herring configuration
        
        Returns:
            Modified documents with red herrings
        """
        if not config.get("enabled", True):
            logger.info("⏭️  Red herrings disabled in config")
            return documents
        
        logger.info("🎭 Adding red herrings (subtle false leads)...")
        
        min_herrings = config.get("min_false_leads", 2)
        max_herrings = config.get("max_false_leads", 3)
        
        # Determine how many red herrings to add
        num_herrings = random.randint(min_herrings, max(min_herrings, min(max_herrings, len(documents) // 5)))
        
        logger.info(f"   Adding {num_herrings} red herring(s)")
        
        # Add each red herring
        for i in range(num_herrings):
            documents = self._add_single_herring(documents, i + 1)
        
        logger.info(f"✅ Red herrings added successfully!")
        return documents
    
    def _add_single_herring(
        self,
        documents: List[Dict[str, Any]],
        herring_num: int
    ) -> List[Dict[str, Any]]:
        """
        Add one red herring to a random document.
        
        Args:
            documents: List of documents
            herring_num: Which herring (for logging)
        
        Returns:
            Modified documents
        """
        # Select a random document that doesn't already have a red herring
        available_docs = [
            doc for doc in documents
            if not doc.get("has_red_herring", False)
        ]
        
        if not available_docs:
            logger.warning(f"   ⚠️  No available documents for herring {herring_num}")
            return documents
        
        target_doc = random.choice(available_docs)
        doc_type = target_doc["document_type"]
        
        # Choose red herring type
        herring_type = random.choice(self.red_herring_types)
        
        logger.info(f"   Herring {herring_num}: {herring_type} → {target_doc['document_id']} ({doc_type})")
        
        # Apply red herring based on type and document type
        self._apply_herring(target_doc, herring_type)
        
        # Mark document as having a red herring
        target_doc["has_red_herring"] = True
        target_doc["red_herring_type"] = herring_type
        
        return documents
    
    def _apply_herring(self, document: Dict[str, Any], herring_type: str) -> None:
        """
        Apply a specific type of red herring to a document.
        
        Args:
            document: Document to modify
            herring_type: Type of red herring to add
        
        Modifies document in-place.
        """
        doc_type = document["document_type"]
        fields = document.get("fields", {})
        
        if herring_type == "suspicious_timing":
            self._add_suspicious_timing(document, fields, doc_type)
        
        elif herring_type == "false_alibi":
            self._add_false_alibi(document, fields, doc_type)
        
        elif herring_type == "misleading_reference":
            self._add_misleading_reference(document, fields, doc_type)
        
        elif herring_type == "red_herring_character":
            self._add_suspicious_character(document, fields, doc_type)
        
        elif herring_type == "coincidental_evidence":
            self._add_coincidental_evidence(document, fields, doc_type)
    
    def _add_suspicious_timing(self, document: Dict[str, Any], fields: Dict[str, Any], doc_type: str) -> None:
        """Add suspicious timing that seems relevant but isn't."""
        
        if doc_type == "badge_log" and "entries" in fields and isinstance(fields["entries"], list):
            # Add entry with suspicious but innocent timing
            if fields["entries"]:
                suspicious_entry = {
                    "badge_number": str(random.randint(1000, 9999)),
                    "name": random.choice(["Alex Chen", "Jordan Lee", "Pat Morgan"]),
                    "entry_time": fields["entries"][0].get("entry_time", "02:30:00"),
                    "location": random.choice(["Parking Lot", "Main Entrance", "Loading Dock"]),
                    "notes": "Normal access"
                }
                fields["entries"].insert(1, suspicious_entry)
        
        elif doc_type == "email" and "body" in fields:
            # Add time reference that seems suspicious
            fields["body"] += "\n\nP.S. Sorry I was late yesterday around 2:30 AM - had to finish some urgent work."
    
    def _add_false_alibi(self, document: Dict[str, Any], fields: Dict[str, Any], doc_type: str) -> None:
        """Add a false alibi for an innocent person."""
        
        if doc_type == "email" and "body" in fields:
            innocent_names = ["Michael Brown", "Jennifer White", "David Kim"]
            name = random.choice(innocent_names)
            fields["body"] += f"\n\n{name} was with me the whole evening at the quarterly meeting. Can confirm."
        
        elif doc_type == "witness_statement" and "statement" in fields:
            fields["statement"] += "\n\nI saw Thomas in the break room at the time in question. He couldn't have been involved."
    
    def _add_misleading_reference(self, document: Dict[str, Any], fields: Dict[str, Any], doc_type: str) -> None:
        """Add reference to irrelevant document or event."""
        
        if doc_type == "internal_memo" and "content" in fields:
            fields["content"] += "\n\nPlease review the security footage from camera 7. Something seemed off."
        
        elif doc_type == "email" and "body" in fields:
            fields["body"] += "\n\nBy the way, did you see the memo about the missing equipment? Might be related."
    
    def _add_suspicious_character(self, document: Dict[str, Any], fields: Dict[str, Any], doc_type: str) -> None:
        """Mention a suspicious but innocent character."""
        
        suspicious_names = ["Marcus Rivera", "Olivia Santos", "Ryan Foster"]
        name = random.choice(suspicious_names)
        
        if doc_type == "diary" and "content" in fields:
            fields["content"] += f"\n\nI keep seeing {name} lurking around at odd hours. What's their deal?"
        
        elif doc_type == "email" and "body" in fields:
            fields["body"] += f"\n\nHas anyone else noticed {name} acting strangely lately?"
        
        elif doc_type == "witness_statement" and "statement" in fields:
            fields["statement"] += f"\n\nI did notice {name} leaving the building in a hurry that night."
    
    def _add_coincidental_evidence(self, document: Dict[str, Any], fields: Dict[str, Any], doc_type: str) -> None:
        """Add evidence that seems incriminating but is coincidental."""
        
        if doc_type == "receipt" and "items" in fields:
            # Add suspicious but innocent purchase
            if isinstance(fields["items"], list):
                fields["items"].append({
                    "item": "USB Drive (32GB)",
                    "quantity": 1,
                    "price": "$19.99",
                    "notes": "For backup purposes"
                })
        
        elif doc_type == "phone_record" and "calls" in fields:
            # Add call to suspicious number
            if isinstance(fields["calls"], list):
                fields["calls"].append({
                    "number": "+1-555-0" + str(random.randint(100, 999)),
                    "duration": f"{random.randint(1, 5)} min",
                    "time": "02:25 AM",
                    "type": "outgoing"
                })
        
        elif doc_type == "surveillance_log" and "entries" in fields:
            # Add suspicious but innocent activity
            if isinstance(fields["entries"], list):
                fields["entries"].append({
                    "time": "02:20:00",
                    "event": "Individual accessing restricted area",
                    "camera": "Cam-05",
                    "notes": "ID verified - authorized personnel"
                })

