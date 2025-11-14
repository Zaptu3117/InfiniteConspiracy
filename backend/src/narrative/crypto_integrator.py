"""Cryptography Integration - add encryption with cross-referenced keys."""

import logging
import random
from typing import List, Dict, Any
from ..documents.cryptography import CipherManager


logger = logging.getLogger(__name__)


class CryptoIntegrator:
    """
    Integrate cryptography into generated documents with cross-references.
    
    Strategy:
    - Select 1-2 documents to encrypt
    - Select different documents to hide the cipher keys
    - Add hints in encrypted docs pointing to key locations
    - Insert keys into key-holder documents
    """
    
    def __init__(self):
        self.cipher_manager = CipherManager()
    
    def apply_cryptography(
        self,
        documents: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply cryptography to documents with cross-referenced keys.
        
        Args:
            documents: List of generated documents
            config: Cryptography configuration
        
        Returns:
            Modified documents with encryption applied
        """
        if not config.get("enabled", True):
            logger.info("⏭️  Cryptography disabled in config")
            return documents
        
        logger.info("🔐 Applying cryptography with cross-referenced keys...")
        
        min_encrypted = config.get("min_encrypted_documents", 1)
        max_encrypted = config.get("max_encrypted_documents", 3)
        
        # Determine how many documents to encrypt
        num_to_encrypt = random.randint(min_encrypted, min(max_encrypted, len(documents) // 3))
        
        logger.info(f"   Encrypting {num_to_encrypt} document(s)")
        
        # Apply encryption cycles
        for i in range(num_to_encrypt):
            documents = self._apply_single_encryption(documents, i + 1)
        
        logger.info(f"✅ Cryptography applied successfully!")
        return documents
    
    def _apply_single_encryption(
        self,
        documents: List[Dict[str, Any]],
        cycle_num: int
    ) -> List[Dict[str, Any]]:
        """
        Apply one encryption cycle: select target doc, key doc, encrypt.
        
        Args:
            documents: List of documents
            cycle_num: Which encryption cycle (for logging)
        
        Returns:
            Modified documents
        """
        # Select document to encrypt (not already encrypted)
        available_targets = [
            doc for doc in documents 
            if not doc.get("cipher_info", {}).get("encrypted", False)
        ]
        
        if len(available_targets) < 2:
            logger.warning(f"   ⚠️  Not enough documents for encryption cycle {cycle_num}")
            return documents
        
        target_doc = random.choice(available_targets)
        
        # Select document to hold the key (different from target)
        available_key_holders = [
            doc for doc in documents 
            if doc["document_id"] != target_doc["document_id"]
        ]
        
        key_holder_doc = random.choice(available_key_holders)
        
        # Choose cipher type
        cipher_type = random.choice(["caesar", "vigenere"])
        
        # Generate cipher key
        if cipher_type == "caesar":
            cipher_key = random.randint(1, 25)
            key_text = f"shift_{cipher_key}"
        elif cipher_type == "vigenere":
            keywords = ["CIPHER", "SECRET", "MYSTERY", "HIDDEN", "ENCODE", "PUZZLE"]
            cipher_key = random.choice(keywords)
            key_text = cipher_key
        else:
            return documents
        
        logger.info(f"   Cycle {cycle_num}: {cipher_type.upper()} cipher")
        logger.info(f"      Target: {target_doc['document_id']} ({target_doc['document_type']})")
        logger.info(f"      Key holder: {key_holder_doc['document_id']} ({key_holder_doc['document_type']})")
        
        # Apply encryption to target document
        fields_to_encrypt = self._select_fields_to_encrypt(target_doc)
        target_doc, cipher_info = self.cipher_manager.apply_cipher(
            target_doc,
            cipher_type,
            cipher_key,
            fields_to_encrypt
        )
        
        # Add hint to target document about where to find key
        hint = self._generate_key_hint(key_holder_doc, cipher_type)
        cipher_info["key_hint"] = hint
        cipher_info["key_location"] = key_holder_doc["document_id"]
        target_doc["cipher_info"] = cipher_info
        
        logger.info(f"      Encrypted fields: {', '.join(fields_to_encrypt)}")
        logger.info(f"      Hint: {hint}")
        
        # Insert key into key holder document
        self._insert_key_into_document(key_holder_doc, key_text, cipher_type)
        
        return documents
    
    def _select_fields_to_encrypt(self, document: Dict[str, Any]) -> List[str]:
        """
        Select which fields of a document to encrypt.
        
        Args:
            document: Document to analyze
        
        Returns:
            List of field names to encrypt
        """
        doc_type = document["document_type"]
        fields = document.get("fields", {})
        
        # Define encryptable fields per document type
        encryptable_by_type = {
            "email": ["body", "subject"],
            "diary": ["content", "entry"],
            "internal_memo": ["content", "message"],
            "witness_statement": ["statement", "testimony"],
            "police_report": ["notes", "description"],
            "newspaper": ["article", "content"],
            "medical_record": ["diagnosis", "notes"],
            "receipt": ["items", "notes"],
        }
        
        candidates = []
        for field_name in encryptable_by_type.get(doc_type, []):
            if field_name in fields and isinstance(fields[field_name], str):
                candidates.append(field_name)
        
        # If no specific fields, try common ones
        if not candidates:
            for field_name in ["content", "body", "text", "message", "notes"]:
                if field_name in fields and isinstance(fields[field_name], str):
                    candidates.append(field_name)
        
        # Return 1-2 fields to encrypt
        if candidates:
            num_to_encrypt = min(random.randint(1, 2), len(candidates))
            return random.sample(candidates, num_to_encrypt)
        
        return []
    
    def _generate_key_hint(
        self,
        key_holder_doc: Dict[str, Any],
        cipher_type: str
    ) -> str:
        """
        Generate a hint about where to find the cipher key.
        
        Args:
            key_holder_doc: Document containing the key
            cipher_type: Type of cipher
        
        Returns:
            Hint string
        """
        doc_type = key_holder_doc["document_type"]
        doc_id = key_holder_doc["document_id"]
        
        # Extract meaningful identifier from doc_id (like "badge_log", "email_02")
        doc_identifier = doc_id.split("_", 1)[1] if "_" in doc_id else doc_id
        
        hints_by_type = {
            "email": [
                f"The key is mentioned in the {doc_identifier} correspondence",
                f"Check the {doc_identifier} for the cipher shift",
                f"Email {doc_identifier} contains the decryption key"
            ],
            "badge_log": [
                f"The shift number appears in the {doc_identifier}",
                f"Check badge entry in {doc_identifier} for the key",
                f"The {doc_identifier} has the cipher value"
            ],
            "diary": [
                f"The keyword is in the {doc_identifier} entry",
                f"See the {doc_identifier} for the cipher keyword",
                f"Diary {doc_identifier} mentions the key"
            ],
            "police_report": [
                f"The key is noted in the {doc_identifier}",
                f"Check report {doc_identifier} for cipher details",
                f"Police {doc_identifier} contains the shift value"
            ],
        }
        
        specific_hints = hints_by_type.get(doc_type, [
            f"The cipher key is in document {doc_identifier}",
            f"Check {doc_identifier} for decryption information",
            f"Document {doc_identifier} holds the key"
        ])
        
        return random.choice(specific_hints)
    
    def _insert_key_into_document(
        self,
        document: Dict[str, Any],
        key_text: str,
        cipher_type: str
    ) -> None:
        """
        Insert the cipher key into a document in a subtle way.
        
        Args:
            document: Document to modify
            key_text: The cipher key to insert
            cipher_type: Type of cipher
        
        Modifies document in-place.
        """
        doc_type = document["document_type"]
        fields = document.get("fields", {})
        
        # Create subtle key insertion based on doc type and cipher type
        if cipher_type == "caesar":
            # For Caesar, key is a number - can be embedded as badge number, room number, etc.
            shift_value = key_text.split("_")[1]  # Extract number from "shift_13"
            
            if doc_type == "badge_log" and "entries" in fields and isinstance(fields["entries"], list):
                # Add to badge number or room number
                if fields["entries"]:
                    entry = fields["entries"][0]
                    if "badge_number" in entry:
                        # Add note about shift
                        if "notes" not in entry:
                            entry["notes"] = f"Shift code: {shift_value}"
                    
            elif doc_type == "email":
                # Add to signature or PS
                if "body" in fields:
                    fields["body"] += f"\n\nP.S. Remember code {shift_value} for the archive system."
            
            else:
                # Generic insertion
                if "notes" in fields:
                    fields["notes"] += f" [Code: {shift_value}]"
                elif "body" in fields and isinstance(fields["body"], str):
                    fields["body"] += f"\n\n[Reference code: {shift_value}]"
        
        elif cipher_type == "vigenere":
            # For Vigenère, key is a word - can be embedded in text, titles, etc.
            keyword = key_text
            
            if doc_type == "newspaper" and "headline" in fields:
                # Add keyword to headline subtly
                fields["headline"] += f": {keyword} Investigation Continues"
            
            elif doc_type == "email" and "subject" in fields:
                # Add to subject
                fields["subject"] += f" [{keyword}]"
            
            elif doc_type == "diary":
                # Add as thought or note
                if "content" in fields:
                    fields["content"] += f"\n\nRemember the keyword: {keyword}."
            
            else:
                # Generic insertion
                if "notes" in fields:
                    fields["notes"] += f" Keyword: {keyword}."
                elif "body" in fields and isinstance(fields["body"], str):
                    fields["body"] += f"\n\n[Keyword: {keyword}]"
        
        logger.info(f"      Key inserted into {document['document_id']}")

