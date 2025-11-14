"""Cryptography utilities for document encryption."""

import logging
import random
from typing import Dict, Any, List, Tuple


logger = logging.getLogger(__name__)


class CipherManager:
    """Manage cipher encryption and key distribution."""
    
    def __init__(self):
        self.cipher_types = ["caesar", "substitution", "vigenere"]
    
    def caesar_encrypt(self, text: str, shift: int) -> str:
        """Caesar cipher encryption."""
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - base + shift) % 26
                result.append(chr(base + shifted))
            else:
                result.append(char)
        return ''.join(result)
    
    def caesar_decrypt(self, text: str, shift: int) -> str:
        """Caesar cipher decryption."""
        return self.caesar_encrypt(text, -shift)
    
    def vigenere_encrypt(self, text: str, keyword: str) -> str:
        """Vigenère cipher encryption."""
        result = []
        keyword = keyword.upper()
        key_index = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(keyword[key_index % len(keyword)]) - ord('A')
                encrypted = (ord(char) - base + shift) % 26
                result.append(chr(base + encrypted))
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def vigenere_decrypt(self, text: str, keyword: str) -> str:
        """Vigenère cipher decryption."""
        result = []
        keyword = keyword.upper()
        key_index = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(keyword[key_index % len(keyword)]) - ord('A')
                decrypted = (ord(char) - base - shift) % 26
                result.append(chr(base + decrypted))
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def apply_cipher(
        self,
        document: Dict[str, Any],
        cipher_type: str,
        cipher_key: Any,
        fields_to_encrypt: List[str]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Apply cipher to specific fields in a document.
        
        Args:
            document: Document dict
            cipher_type: Type of cipher (caesar, vigenere, etc.)
            cipher_key: Key for the cipher
            fields_to_encrypt: List of field names to encrypt
        
        Returns:
            Tuple of (modified document, cipher info)
        """
        logger.debug(f"Applying {cipher_type} cipher to {document['document_id']}")
        
        for field in fields_to_encrypt:
            if field in document["fields"]:
                original_text = document["fields"][field]
                
                if cipher_type == "caesar":
                    encrypted_text = self.caesar_encrypt(original_text, cipher_key)
                elif cipher_type == "vigenere":
                    encrypted_text = self.vigenere_encrypt(original_text, cipher_key)
                else:
                    encrypted_text = original_text
                
                document["fields"][field] = encrypted_text
        
        cipher_info = {
            "encrypted": True,
            "cipher_type": cipher_type,
            "encrypted_sections": fields_to_encrypt,
            "hint": self._generate_hint(cipher_type)
        }
        
        return document, cipher_info
    
    def distribute_cipher_keys(
        self,
        documents: List[Dict[str, Any]],
        cipher_type: str,
        cipher_key: Any,
        num_fragments: int = 3
    ) -> List[int]:
        """
        Distribute cipher key across multiple documents.
        
        Args:
            documents: List of all documents
            cipher_type: Type of cipher
            cipher_key: The key to distribute
            num_fragments: Number of documents to split key across
        
        Returns:
            List of document indices that contain key fragments
        """
        if cipher_type == "caesar":
            # For Caesar, just put the shift value in a document
            key_hint = f"The shift is {cipher_key}"
        elif cipher_type == "vigenere":
            # For Vigenère, split keyword across documents
            key_hint = f"The keyword is: {cipher_key}"
        else:
            key_hint = str(cipher_key)
        
        # Select random documents to hide key fragments
        available_indices = list(range(len(documents)))
        random.shuffle(available_indices)
        key_holder_indices = available_indices[:num_fragments]
        
        logger.debug(f"Key distributed across documents: {key_holder_indices}")
        
        return key_holder_indices
    
    def _generate_hint(self, cipher_type: str) -> str:
        """Generate a hint for decryption."""
        hints = {
            "caesar": "Check the badge access logs for the key number",
            "vigenere": "The keyword is hidden in the newspaper headline",
            "substitution": "Cross-reference the three memos for the cipher alphabet"
        }
        return hints.get(cipher_type, "Find the key in the documents")

