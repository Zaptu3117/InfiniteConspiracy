"""Phrase-Level Encryptor - encrypts specific phrases within documents."""

import logging
import random
from typing import Dict, Any, List, Optional
from models.conspiracy import CryptoKey


logger = logging.getLogger(__name__)


class PhraseEncryptor:
    """Encrypt specific phrases within document content."""
    
    def __init__(self):
        """Initialize encryptor."""
        pass
    
    def encrypt_phrase(
        self,
        plaintext: str,
        encryption_type: str,
        key: str
    ) -> str:
        """
        Encrypt a phrase using specified cipher.
        
        Args:
            plaintext: The text to encrypt
            encryption_type: "caesar" or "vigenere"
            key: The encryption key
        
        Returns:
            Encrypted text
        """
        if encryption_type == "caesar":
            # For Caesar, key should be a number
            try:
                shift = int(key) if isinstance(key, int) else self._key_to_shift(key)
            except:
                shift = 13  # Default ROT13
            return self._caesar_cipher(plaintext, shift)
        
        elif encryption_type == "vigenere":
            return self._vigenere_cipher(plaintext, key)
        
        else:
            logger.warning(f"Unknown encryption type: {encryption_type}, using Caesar")
            return self._caesar_cipher(plaintext, 13)
    
    def decrypt_phrase(
        self,
        ciphertext: str,
        encryption_type: str,
        key: str
    ) -> str:
        """
        Decrypt a phrase.
        
        Args:
            ciphertext: The encrypted text
            encryption_type: "caesar" or "vigenere"
            key: The decryption key
        
        Returns:
            Decrypted text
        """
        if encryption_type == "caesar":
            try:
                shift = int(key) if isinstance(key, int) else self._key_to_shift(key)
            except:
                shift = 13
            return self._caesar_cipher(ciphertext, -shift)  # Negative shift to decrypt
        
        elif encryption_type == "vigenere":
            return self._vigenere_decipher(ciphertext, key)
        
        return ciphertext
    
    def embed_encrypted_phrase(
        self,
        document_content: str,
        plaintext: str,
        crypto_key: CryptoKey,
        encryption_type: str
    ) -> tuple[str, str]:
        """
        Embed an encrypted phrase into document content.
        
        Args:
            document_content: The document text
            plaintext: The phrase to encrypt
            crypto_key: The crypto key object
            encryption_type: Type of encryption
        
        Returns:
            Tuple of (modified_content, encrypted_phrase)
        """
        # Encrypt the phrase
        encrypted = self.encrypt_phrase(plaintext, encryption_type, crypto_key.key_value)
        
        # Add hint about encryption
        hint_text = f" [Encrypted note: {encrypted}]"
        if crypto_key.inference_description:
            hint_text += f" (Key hint: {crypto_key.inference_description})"
        
        # Insert into content
        modified_content = document_content + hint_text
        
        return modified_content, encrypted
    
    def _key_to_shift(self, key: str) -> int:
        """Convert a text key to a Caesar shift value."""
        # Sum ASCII values and mod 26
        return sum(ord(c) for c in key.upper()) % 26
    
    def _caesar_cipher(self, text: str, shift: int) -> str:
        """Apply Caesar cipher to text."""
        result = []
        
        for char in text:
            if char.isalpha():
                # Determine if uppercase or lowercase
                base = ord('A') if char.isupper() else ord('a')
                # Shift character
                shifted = (ord(char) - base + shift) % 26
                result.append(chr(base + shifted))
            else:
                # Keep non-alphabetic characters unchanged
                result.append(char)
        
        return ''.join(result)
    
    def _vigenere_cipher(self, plaintext: str, key: str) -> str:
        """Apply Vigenere cipher to text."""
        result = []
        key = key.upper()
        key_index = 0
        
        for char in plaintext:
            if char.isalpha():
                # Determine if uppercase or lowercase
                base = ord('A') if char.isupper() else ord('a')
                
                # Get key character shift
                key_char = key[key_index % len(key)]
                shift = ord(key_char) - ord('A')
                
                # Apply shift
                shifted = (ord(char) - base + shift) % 26
                result.append(chr(base + shifted))
                
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _vigenere_decipher(self, ciphertext: str, key: str) -> str:
        """Decrypt Vigenere cipher."""
        result = []
        key = key.upper()
        key_index = 0
        
        for char in ciphertext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                
                # Get key character shift
                key_char = key[key_index % len(key)]
                shift = ord(key_char) - ord('A')
                
                # Apply negative shift (decrypt)
                shifted = (ord(char) - base - shift) % 26
                result.append(chr(base + shifted))
                
                key_index += 1
            else:
                result.append(char)
        
        return ''.join(result)


# Test the encryptor
if __name__ == "__main__":
    encryptor = PhraseEncryptor()
    
    # Test Caesar
    plaintext = "The ritual begins at midnight"
    encrypted_caesar = encryptor.encrypt_phrase(plaintext, "caesar", "13")
    decrypted_caesar = encryptor.decrypt_phrase(encrypted_caesar, "caesar", "13")
    
    print(f"Original: {plaintext}")
    print(f"Caesar(13): {encrypted_caesar}")
    print(f"Decrypted: {decrypted_caesar}")
    print()
    
    # Test Vigenere
    key = "SECRETKEY"
    encrypted_vig = encryptor.encrypt_phrase(plaintext, "vigenere", key)
    decrypted_vig = encryptor.decrypt_phrase(encrypted_vig, "vigenere", key)
    
    print(f"Original: {plaintext}")
    print(f"Vigenere({key}): {encrypted_vig}")
    print(f"Decrypted: {decrypted_vig}")

