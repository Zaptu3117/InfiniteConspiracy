"""Cryptographic Node Generator - inference-based keys and encrypted evidence."""

import logging
import random
from typing import List, Dict, Any, Optional
from models.conspiracy import (
    EvidenceNode,
    InferenceNode,
    CryptoKey,
    EvidenceType,
    AnswerDimension,
    ConspiracyPremise
)


logger = logging.getLogger(__name__)


CRYPTO_KEY_PROMPT = """You are creating inference-based cryptographic keys for a conspiracy mystery.

CONSPIRACY CONTEXT:
{conspiracy_context}

CHARACTERS (who might have keys):
{characters_summary}

YOUR TASK:
Generate {num_keys} cryptographic keys that require INFERENCE from character backstories.

EXAMPLES OF INFERENCE-BASED KEYS:
- "what father always said about trust" → Character backstory reveals: "Never trust the system"
- "the promise we made that night" → Timeline shows shared oath: "We swore to protect the truth"
- "the night everything changed" → Past event description: "The Blackwater Incident of 2019"
- "mother's final warning" → Character history: "Beware the ones who smile brightest"
- "the place where it all began" → Location reference: "The Obsidian Chamber beneath headquarters"

IMPORTANT:
- Keys should be OBSCURE references, not obvious
- Require understanding character history/relationships
- Not simple facts like pet names or birthdays
- Should feel meaningful to the character
- Discoverable but require reading and inference

For each key, provide:
1. inference_description: The obscure reference (e.g., "what father taught me about loyalty")
2. actual_key: The text that becomes the cipher key (e.g., "FAMILY FIRST")
3. hint_text: How it's hinted in documents (e.g., "Remember what he always said...")
4. character_name: Which character's backstory contains this
5. discovery_method: How to discover it (e.g., "Read character's diary entry about father")

Output JSON array with {num_keys} key objects:
[
  {{
    "inference_description": "Obscure reference requiring inference",
    "actual_key": "THE ACTUAL KEY TEXT",
    "hint_text": "How it's hinted in encrypted document",
    "character_name": "Character Name",
    "discovery_method": "How to find the key"
  }}
]"""


CRYPTO_EVIDENCE_PROMPT = """You are creating encrypted evidence for a conspiracy mystery.

CONSPIRACY CONTEXT:
{conspiracy_context}

CRYPTO KEY:
{key_info}

YOUR TASK:
Generate {num_phrases} phrases/sentences that should be encrypted in documents.

IMPORTANT:
- Phrases should contain KEY INFORMATION about the conspiracy
- Should reveal aspects of WHAT (goal) or HOW (method)
- Keep phrases 3-10 words long
- Should feel like secret communications or hidden notes
- Make them meaningful to the conspiracy

Examples:
- "The ritual begins at midnight on the solstice"
- "Agent Torres has infiltrated the Directorate"
- "The artifact is hidden in Vault Seven"
- "Phase three activates when all seals break"

Output JSON array:
[
  {{
    "plaintext": "The actual message",
    "doc_type": "email|diary|internal_memo|report",
    "context": "Where this phrase appears in document"
  }}
]"""


class CryptoNodeGenerator:
    """Generate cryptographic evidence with inference-based keys."""
    
    def __init__(self, llm_client):
        """
        Initialize generator.
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
    
    async def generate_crypto_chain(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        characters: List[Dict[str, Any]],
        architecture: Any,
        contributes_to: AnswerDimension,
        config: Dict[str, Any] = None
    ) -> tuple[List[EvidenceNode], List[InferenceNode], List[CryptoKey]]:
        """
        Generate cryptographic chain nodes.
        
        Args:
            subgraph_id: Sub-graph identifier
            premise: Conspiracy premise
            characters: Character list
            architecture: Sub-graph architecture
            contributes_to: Which answer dimension (WHAT/HOW)
            config: Optional configuration
        
        Returns:
            Tuple of (evidence_nodes, inference_nodes, crypto_keys)
        """
        config = config or {}
        
        logger.info(f"   Generating crypto chain {subgraph_id}...")
        
        # Determine number of encrypted phrases needed
        num_phrases = random.randint(2, 3)  # 2-3 encrypted phrases per chain
        
        # Generate one key per phrase to ensure all phrases have keys
        num_keys = num_phrases
        
        # Generate crypto keys
        crypto_keys = await self._generate_crypto_keys(
            subgraph_id,
            premise,
            characters,
            num_keys,
            config
        )
        
        # Generate encrypted phrases (with all keys)
        encrypted_evidence = await self._generate_encrypted_phrases(
            subgraph_id,
            premise,
            crypto_keys,  # Pass all keys, not just first one
            num_phrases,
            contributes_to,
            config
        )
        
        # Generate key hint evidence
        key_hint_evidence = self._generate_key_hints(subgraph_id, crypto_keys)
        
        # Combine evidence nodes
        evidence_nodes = encrypted_evidence + key_hint_evidence
        
        # Generate inference nodes for key discovery and decryption
        inference_nodes = self._generate_crypto_inferences(
            subgraph_id,
            crypto_keys,
            evidence_nodes,
            contributes_to
        )
        
        return evidence_nodes, inference_nodes, crypto_keys
    
    async def _generate_crypto_keys(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        characters: List[Dict[str, Any]],
        num_keys: int,
        config: Dict[str, Any]
    ) -> List[CryptoKey]:
        """Generate inference-based crypto keys."""
        
        conspiracy_context = f"""
Conspiracy: {premise.conspiracy_name}
Goal: {premise.what}
Method: {premise.how}
"""
        
        characters_summary = "\n".join([
            f"- {char.get('name', 'Unknown')}: {char.get('role', 'Unknown role')}"
            for char in characters[:5]
        ]) if characters else "Characters not yet generated"
        
        # Build prompt
        prompt = CRYPTO_KEY_PROMPT.format(
            conspiracy_context=conspiracy_context,
            characters_summary=characters_summary,
            num_keys=num_keys
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1500)
            )
            
            # Parse response
            if isinstance(response, list):
                keys_data = response
            else:
                keys_data = response.get("keys", [])
            
            # Create CryptoKey objects
            crypto_keys = []
            for i, data in enumerate(keys_data[:num_keys]):
                key = CryptoKey(
                    key_id=f"{subgraph_id}_key_{i}",
                    key_value=data.get("actual_key", "SECRETKEY"),
                    inference_description=data.get("inference_description", "the hidden truth"),
                    character_name=data.get("character_name"),
                    hint_documents=[],  # Will be filled later
                    discoverable=True,
                    unlocks_node_id=None  # Will be set later
                )
                crypto_keys.append(key)
                
                logger.info(f"      Generated key: '{key.inference_description}' → '{key.key_value}'")
            
            return crypto_keys
        
        except Exception as e:
            logger.error(f"   ❌ Crypto key generation failed: {e}")
            return self._create_fallback_keys(subgraph_id, num_keys)
    
    async def _generate_encrypted_phrases(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        crypto_keys: List[CryptoKey],
        num_phrases: int,
        contributes_to: AnswerDimension,
        config: Dict[str, Any]
    ) -> List[EvidenceNode]:
        """Generate phrases that will be encrypted."""
        
        if not crypto_keys:
            return []
        
        # Focus on WHAT or HOW based on contribution
        if contributes_to == AnswerDimension.WHAT:
            focus = f"Goal: {premise.what}"
        else:
            focus = f"Method: {premise.how}"
        
        conspiracy_context = f"""
Conspiracy: {premise.conspiracy_name}
{focus}
"""
        
        key_info = f"Key reference: {crypto_keys[0].inference_description}"
        
        # Build prompt
        prompt = CRYPTO_EVIDENCE_PROMPT.format(
            conspiracy_context=conspiracy_context,
            key_info=key_info,
            num_phrases=num_phrases
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1000)
            )
            
            # Parse response
            if isinstance(response, list):
                phrases_data = response
            else:
                phrases_data = response.get("phrases", [])
            
            # Create evidence nodes - one per phrase, each with its own key
            evidence_nodes = []
            for i, data in enumerate(phrases_data[:num_phrases]):
                # Get the corresponding key for this phrase (one key per phrase)
                crypto_key = crypto_keys[i] if i < len(crypto_keys) else crypto_keys[0]
                
                # The encrypted phrase will be added during document generation
                node = EvidenceNode(
                    node_id=f"{subgraph_id}_crypto_ev_{i}",
                    evidence_type=EvidenceType.CRYPTOGRAPHIC,
                    content=data.get("plaintext", "Secret message"),
                    encrypted_phrase=data.get("plaintext"),  # Will be encrypted later
                    encryption_type=random.choice(["caesar", "vigenere"]),
                    key_hint=f"The key is: {crypto_key.inference_description}",
                    assigned_doc_type=data.get("doc_type", "email"),
                    isolated=True,
                    importance="key",
                    subgraph_id=subgraph_id
                )
                evidence_nodes.append(node)
                
                # Link this specific key to this specific node
                crypto_key.unlocks_node_id = node.node_id
            
            return evidence_nodes
        
        except Exception as e:
            logger.error(f"   ❌ Encrypted phrase generation failed: {e}")
            return self._create_fallback_encrypted_evidence(subgraph_id, num_phrases, crypto_keys[0] if crypto_keys else None)
    
    def _generate_key_hints(
        self,
        subgraph_id: str,
        crypto_keys: List[CryptoKey]
    ) -> List[EvidenceNode]:
        """Generate evidence nodes that hint at keys."""
        hint_nodes = []
        
        for i, key in enumerate(crypto_keys):
            # Create character backstory hint
            hint_node = EvidenceNode(
                node_id=f"{subgraph_id}_key_hint_{i}",
                evidence_type=EvidenceType.CRYPTOGRAPHIC,
                content=f"Character backstory reveals: {key.inference_description}",
                assigned_doc_type=random.choice(["diary", "witness_statement", "internal_memo"]),
                isolated=True,
                importance="key",
                subgraph_id=subgraph_id
            )
            hint_nodes.append(hint_node)
            
            # Add to key's hint documents
            key.hint_documents.append(hint_node.node_id)
        
        return hint_nodes
    
    def _generate_crypto_inferences(
        self,
        subgraph_id: str,
        crypto_keys: List[CryptoKey],
        evidence_nodes: List[EvidenceNode],
        contributes_to: AnswerDimension
    ) -> List[InferenceNode]:
        """Generate inference nodes for key discovery and decryption."""
        inferences = []
        
        # Inference 1: Discover the key through inference
        if crypto_keys:
            key = crypto_keys[0]
            inf1 = InferenceNode(
                node_id=f"{subgraph_id}_crypto_inf_0",
                inference=f"Character analysis reveals the key: {key.key_value}",
                reasoning_type="inference_synthesis",
                parent_node_ids=[node.node_id for node in evidence_nodes if "hint" in node.node_id],
                required_document_ids=[],
                contributes_to=contributes_to,
                subgraph_id=subgraph_id
            )
            inferences.append(inf1)
        
        # Inference 2: Decrypt the message
        inf2 = InferenceNode(
            node_id=f"{subgraph_id}_crypto_inf_1",
            inference="Decrypted message reveals conspiracy details",
            reasoning_type="decryption",
            parent_node_ids=[node.node_id for node in evidence_nodes],
            required_document_ids=[],
            contributes_to=contributes_to,
            subgraph_id=subgraph_id
        )
        inferences.append(inf2)
        
        # Inference 3: Interpret the decoded message
        inf3 = InferenceNode(
            node_id=f"{subgraph_id}_crypto_inf_2",
            inference="Decoded information connects to conspiracy goal/method",
            reasoning_type="interpretation",
            parent_node_ids=[inf2.node_id],
            required_document_ids=[],
            contributes_to=contributes_to,
            subgraph_id=subgraph_id
        )
        inferences.append(inf3)
        
        return inferences
    
    def _create_fallback_keys(self, subgraph_id: str, num_keys: int) -> List[CryptoKey]:
        """Create fallback crypto keys."""
        fallback_keys = [
            ("what father always warned about", "TRUST NO ONE", "Agent Reeves"),
            ("the promise we made that night", "PROTECT THE TRUTH", "Dr. Kross"),
            ("mother's dying words", "THE VEIL MUST FALL", "Director Varela")
        ]
        
        keys = []
        for i in range(min(num_keys, len(fallback_keys))):
            inference_desc, key_value, char_name = fallback_keys[i]
            key = CryptoKey(
                key_id=f"{subgraph_id}_key_{i}",
                key_value=key_value,
                inference_description=inference_desc,
                character_name=char_name,
                hint_documents=[],
                discoverable=True
            )
            keys.append(key)
        
        return keys
    
    def _create_fallback_encrypted_evidence(
        self,
        subgraph_id: str,
        num_phrases: int,
        crypto_key: Optional[CryptoKey]
    ) -> List[EvidenceNode]:
        """Create fallback encrypted evidence."""
        fallback_phrases = [
            "The ritual begins at the convergence point",
            "Agent Torres has the final artifact",
            "Phase three activates on the solstice",
            "The vault contains the proof we need"
        ]
        
        nodes = []
        for i in range(min(num_phrases, len(fallback_phrases))):
            node = EvidenceNode(
                node_id=f"{subgraph_id}_crypto_ev_{i}",
                evidence_type=EvidenceType.CRYPTOGRAPHIC,
                content=fallback_phrases[i],
                encrypted_phrase=fallback_phrases[i],
                encryption_type="caesar",
                key_hint=f"Key: {crypto_key.inference_description}" if crypto_key else None,
                assigned_doc_type="email",
                isolated=True,
                importance="key",
                subgraph_id=subgraph_id
            )
            nodes.append(node)
        
        return nodes

