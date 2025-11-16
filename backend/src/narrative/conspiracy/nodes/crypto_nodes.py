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
    ConspiracyPremise,
    MysteryAnswer
)


logger = logging.getLogger(__name__)


CRYPTO_KEY_PROMPT = """You are creating inference-based cryptographic keys for a conspiracy mystery.

CONSPIRACY CONTEXT:
{conspiracy_context}

CHARACTERS (who might have keys):
{characters_summary}

YOUR TASK:
Generate {num_keys} cryptographic keys that require INFERENCE from character backstories.

⚠️ CRITICAL: Keys must be SHORT (2-4 words max) - they are PASSWORDS!

EXAMPLES OF GOOD INFERENCE-BASED KEYS:
- "mother's lullaby phrase" → Character backstory: "mother sang about silver tide" → Key: "silver tide"
- "father's warning" → Character history: "father said never trust" → Key: "never trust"  
- "the oath we swore" → Shared memory: "we promised to protect truth" → Key: "protect truth"
- "childhood memory" → Diary entry: "hiding beneath broken compass" → Key: "broken compass"
- "the night everything changed" → Timeline: "eclipse over obsidian chamber" → Key: "eclipse obsidian"

IMPORTANT RULES:
✅ Keys MUST be 2-4 words maximum (e.g., "SILVER TIDE", "NEVER TRUST")
✅ Keys should be MEMORABLE phrases, not random words
✅ Require reading MULTIPLE documents to piece together
✅ Obscure but discoverable through character backstory
✅ Should feel meaningful to the character
❌ NO full sentences (e.g., "the object that held the abyss's heart")
❌ NO more than 4 words
❌ NOT obvious facts like pet names or birthdays

For each key, provide:
1. inference_description: The obscure reference (e.g., "mother's lullaby")
2. actual_key: SHORT password 2-4 words (e.g., "silver tide")
3. hint_text: How encrypted doc hints at it (e.g., "Use the phrase from the lullaby")
4. character_name: Which character's backstory contains this
5. discovery_method: How to find it (e.g., "Read character's diary + family letter")

Output JSON array with {num_keys} key objects:
[
  {{
    "inference_description": "Obscure reference requiring inference",
    "actual_key": "short memorable phrase",
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

TARGET PHRASE TO EMBED: "{target_phrase}"
PHRASE TYPE: {phrase_type}

YOUR TASK:
Generate {num_phrases} phrases/sentences that should be encrypted in documents.

CRITICAL REQUIREMENTS:

{embedding_strategy}

IMPORTANT:
- Phrases should contain KEY INFORMATION about the conspiracy
- Keep phrases 5-12 words long
- Should feel like secret communications or operational orders
- Make them meaningful to the conspiracy

Output JSON array with {num_phrases} phrase objects:
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
        answer_template: MysteryAnswer,
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
            answer_template: Answer template with discoverable WHAT/HOW phrases
            config: Optional configuration
        
        Returns:
            Tuple of (evidence_nodes, inference_nodes, crypto_keys)
        """
        config = config or {}
        
        # Log target phrase based on contribution
        target_phrase = answer_template.what if contributes_to == AnswerDimension.WHAT else answer_template.how
        logger.info(f"   Generating crypto chain {subgraph_id}...")
        logger.info(f"      Contributes to: {contributes_to.value}")
        logger.info(f"      Target phrase: \"{target_phrase}\"")
        
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
            answer_template,
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
                max_tokens=config.get("max_tokens", 3000)  # High limit to prevent truncation
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
        answer_template: MysteryAnswer,
        config: Dict[str, Any]
    ) -> List[EvidenceNode]:
        """Generate phrases that will be encrypted, embedding target answer phrase."""
        
        if not crypto_keys:
            return []
        
        # Get target phrase based on contribution
        if contributes_to == AnswerDimension.WHAT:
            target_phrase = answer_template.what
            focus = f"Operation: {answer_template.what}"
        else:
            target_phrase = answer_template.how
            focus = f"Method: {answer_template.how}"
        
        conspiracy_context = f"""
Conspiracy: {premise.conspiracy_name}
{focus}
Context: {premise.what[:200] if contributes_to == AnswerDimension.WHAT else premise.how[:200]}...
"""
        
        key_info = f"Key reference: {crypto_keys[0].inference_description}"
        
        # Determine phrase type and embedding strategy
        if contributes_to == AnswerDimension.WHAT:
            phrase_type = "OPERATION CODENAME"
            embedding_strategy = f"""OPERATION CODENAME CONTAINMENT:
- ONLY 1 message should contain the FULL codename "{target_phrase}"
- Other messages should use PARTIAL references:
  * "the {target_phrase.split()[0]} operation"
  * "the {target_phrase.split()[-1]} protocol"
  * "the operation" / "the mission" / "the project"
  * Internal codenames or nicknames
- This makes the full codename rare and valuable

EXAMPLE (if codename is "Eclipse Veil"):
- Message 1 (FULL): "Operation Eclipse Veil begins at midnight"
- Message 2 (PARTIAL): "The Eclipse protocol activated"
- Message 3 (GENERIC): "The operation proceeds as planned"
"""
        else:  # HOW
            phrase_type = "METHOD/TACTIC"
            embedding_strategy = f"""METHOD EMBEDDING:
- AT LEAST 1 message MUST contain "{target_phrase}" verbatim
- This describes the primary method/tactic
- Embed it naturally in operational orders or technical instructions
- Can be repeated if it's a key tactical phrase

EXAMPLE: "Phase 1: {target_phrase} to establish access"
"""
        
        # Build prompt with target phrase and strategy
        prompt = CRYPTO_EVIDENCE_PROMPT.format(
            conspiracy_context=conspiracy_context,
            key_info=key_info,
            target_phrase=target_phrase,
            phrase_type=phrase_type,
            embedding_strategy=embedding_strategy,
            num_phrases=num_phrases
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 3000)  # High limit to prevent truncation
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
        """
        Generate evidence nodes that contain the actual key phrases.
        
        The document should naturally mention the key phrase so players
        can discover it through character backstory inference.
        """
        hint_nodes = []
        
        for i, key in enumerate(crypto_keys):
            # Create character backstory hint with ACTUAL key phrase
            # Format: "Character backstory reveals: [actual key phrase]"
            # This tells the LLM to naturally weave the key phrase into the character's story
            hint_node = EvidenceNode(
                node_id=f"{subgraph_id}_key_hint_{i}",
                evidence_type=EvidenceType.CRYPTOGRAPHIC,
                content=f"Character backstory reveals: {key.key_value}",
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

