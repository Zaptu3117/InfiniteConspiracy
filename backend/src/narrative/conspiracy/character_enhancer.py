"""Character Enhancer - adds crypto key backstories to characters."""

import logging
import random
from typing import List, Dict, Any
from models.conspiracy import CryptoKey, PoliticalContext


logger = logging.getLogger(__name__)


BACKSTORY_ENHANCEMENT_PROMPT = """You are enhancing a character's backstory to hide cryptographic keys.

CHARACTER:
Name: {char_name}
Role: {char_role}
Current Background: {current_background}

POLITICAL CONTEXT:
{political_summary}

CRYPTO KEYS TO HIDE:
{keys_to_hide}

YOUR TASK:
Enhance the character's backstory to naturally include these key references.

For each key:
- Weave the reference into their personal history
- Make it feel meaningful to the character
- Could be: family sayings, formative events, mentor's wisdom, personal beliefs
- Should require reading and inference to discover

EXAMPLES:
- Key "TRUST NO ONE" → "His father, a former intelligence officer, always warned him: trust no one but family"
- Key "THE VEIL MUST FALL" → "Her mother's dying words echoed in her mind: the veil must fall for truth to emerge"
- Key "PROTECT THE TRUTH" → "The oath they swore that night still binds them: protect the truth at all costs"

Output JSON:
{{
  "enhanced_background": "Updated backstory with key references woven in naturally",
  "key_references": [
    {{
      "key_id": "key ID",
      "reference_text": "How the key appears in backstory",
      "context": "Why this is meaningful to character"
    }}
  ]
}}"""


class CharacterEnhancer:
    """Enhance characters with crypto key backstories."""
    
    def __init__(self, llm_client):
        """
        Initialize enhancer.
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
    
    async def enhance_characters_with_keys(
        self,
        characters: List[Dict[str, Any]],
        crypto_keys: List[CryptoKey],
        political_context: PoliticalContext,
        config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhance characters with crypto key references in backstories.
        
        Args:
            characters: List of character dicts
            crypto_keys: Crypto keys to hide in backstories
            political_context: Political context
            config: Optional configuration
        
        Returns:
            Enhanced character list
        """
        config = config or {}
        
        logger.info("👥 Enhancing characters with crypto keys...")
        logger.info(f"   Characters: {len(characters)}")
        logger.info(f"   Crypto keys to hide: {len(crypto_keys)}")
        
        # Assign keys to characters
        key_assignments = self._assign_keys_to_characters(characters, crypto_keys)
        
        # Enhance each character
        enhanced_characters = []
        for char in characters:
            char_name = char.get("name", "Unknown")
            assigned_keys = key_assignments.get(char_name, [])
            
            if assigned_keys:
                logger.info(f"   Enhancing {char_name} with {len(assigned_keys)} key(s)")
                enhanced = await self._enhance_single_character(
                    char,
                    assigned_keys,
                    political_context,
                    config
                )
                enhanced_characters.append(enhanced)
            else:
                enhanced_characters.append(char)
        
        logger.info(f"   ✅ Enhanced {sum(1 for c in enhanced_characters if 'crypto_keys' in c)} characters")
        logger.info("")
        
        return enhanced_characters
    
    def _assign_keys_to_characters(
        self,
        characters: List[Dict[str, Any]],
        crypto_keys: List[CryptoKey]
    ) -> Dict[str, List[CryptoKey]]:
        """Assign crypto keys to characters."""
        
        assignments = {}
        
        for key in crypto_keys:
            # If key already specifies a character, use that
            if key.character_name:
                target_char = key.character_name
            else:
                # Assign to random character
                if characters:
                    char = random.choice(characters)
                    target_char = char.get("name", "Unknown")
                    key.character_name = target_char
                else:
                    target_char = "Unknown"
            
            if target_char not in assignments:
                assignments[target_char] = []
            assignments[target_char].append(key)
        
        return assignments
    
    async def _enhance_single_character(
        self,
        character: Dict[str, Any],
        crypto_keys: List[CryptoKey],
        political_context: PoliticalContext,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance a single character with crypto keys."""
        
        char_name = character.get("name", "Unknown")
        char_role = character.get("role", "Unknown")
        current_background = character.get("background", "")
        
        # Build keys to hide summary
        keys_summary = "\n".join([
            f"- Key: '{key.key_value}' (Reference: {key.inference_description})"
            for key in crypto_keys
        ])
        
        political_summary = f"""
World: {political_context.world_name}
Tensions: {', '.join(political_context.unresolved_tensions[:2])}
"""
        
        # Build prompt
        prompt = BACKSTORY_ENHANCEMENT_PROMPT.format(
            char_name=char_name,
            char_role=char_role,
            current_background=current_background,
            political_summary=political_summary,
            keys_to_hide=keys_summary
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1500)
            )
            
            # Update character
            enhanced_background = response.get("enhanced_background", current_background)
            key_references = response.get("key_references", [])
            
            character["background"] = enhanced_background
            character["crypto_keys"] = [key.key_id for key in crypto_keys]
            character["key_references"] = key_references
            
            return character
        
        except Exception as e:
            logger.error(f"   ❌ Character enhancement failed for {char_name}: {e}")
            # Return with programmatic enhancement
            return self._enhance_character_programmatically(character, crypto_keys)
    
    def _enhance_character_programmatically(
        self,
        character: Dict[str, Any],
        crypto_keys: List[CryptoKey]
    ) -> Dict[str, Any]:
        """Enhance character programmatically if LLM fails."""
        
        current_background = character.get("background", "")
        
        # Add key references to background
        key_snippets = []
        for key in crypto_keys:
            snippet = f"They often recalled {key.inference_description}: '{key.key_value}'."
            key_snippets.append(snippet)
        
        enhanced_background = current_background + " " + " ".join(key_snippets)
        
        character["background"] = enhanced_background
        character["crypto_keys"] = [key.key_id for key in crypto_keys]
        
        return character

