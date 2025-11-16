"""Convert ConspiracyMystery to Mystery model for blockchain registration."""

import logging
import json
import hashlib
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ConspiracyToMysteryConverter:
    """Convert conspiracy mystery format to blockchain mystery format."""
    
    @staticmethod
    def convert(conspiracy_mystery: Any, expires_in: int = 604800) -> 'Mystery':
        """
        Convert ConspiracyMystery to Mystery model.
        
        Args:
            conspiracy_mystery: ConspiracyMystery object from generation pipeline
            expires_in: Expiration time in seconds (default: 7 days)
        
        Returns:
            Mystery object ready for blockchain registration
        """
        from models import Mystery, MysteryMetadata
        
        logger.info("🔄 Converting ConspiracyMystery to blockchain Mystery format...")
        
        # Extract answer from answer_template (WHO|WHAT|WHY|HOW format)
        answer_parts = [
            conspiracy_mystery.answer_template.who,
            conspiracy_mystery.answer_template.what,
            conspiracy_mystery.answer_template.why,
            conspiracy_mystery.answer_template.how
        ]
        
        # Create pipe-delimited answer (this will be hashed for blockchain)
        answer = "|".join(answer_parts)
        
        logger.info(f"   Answer components:")
        logger.info(f"      WHO: {answer_parts[0][:50]}...")
        logger.info(f"      WHAT: {answer_parts[1][:50]}...")
        logger.info(f"      WHY: {answer_parts[2][:50]}...")
        logger.info(f"      HOW: {answer_parts[3][:50]}...")
        
        # Create proof tree from conspiracy data
        proof_tree = ConspiracyToMysteryConverter._create_proof_tree(conspiracy_mystery)
        
        # Create metadata
        metadata = MysteryMetadata(
            mystery_id=conspiracy_mystery.mystery_id,
            question=conspiracy_mystery.questions.get('who', 'Who orchestrated this conspiracy?'),
            difficulty=conspiracy_mystery.difficulty,
            total_documents=len(conspiracy_mystery.documents),
            total_images=len(conspiracy_mystery.image_clues),
            created_at=int(datetime.fromisoformat(conspiracy_mystery.created_at).timestamp()),
            expires_in=expires_in
        )
        
        # Create Mystery object
        mystery = Mystery(
            metadata=metadata,
            answer=answer,
            proof_tree=proof_tree,
            documents=conspiracy_mystery.documents,
            images=[ic.to_dict() for ic in conspiracy_mystery.image_clues]
        )
        
        # Generate hashes
        mystery.generate_hashes()
        
        logger.info(f"   ✅ Conversion complete")
        logger.info(f"      Mystery ID: {mystery.metadata.mystery_id}")
        logger.info(f"      Answer Hash: {mystery.answer_hash}")
        logger.info(f"      Proof Hash: {mystery.proof_hash}")
        
        return mystery
    
    @staticmethod
    def _create_proof_tree(conspiracy_mystery: Any) -> Dict[str, Any]:
        """
        Create proof tree from conspiracy mystery structure.
        
        The proof tree shows the logical connections between evidence nodes
        and how they lead to the final answer.
        
        Args:
            conspiracy_mystery: ConspiracyMystery object
        
        Returns:
            Proof tree dictionary
        """
        proof_tree = {
            "type": "conspiracy_mystery",
            "mystery_id": conspiracy_mystery.mystery_id,
            "answer": {
                "who": conspiracy_mystery.answer_template.who,
                "what": conspiracy_mystery.answer_template.what,
                "why": conspiracy_mystery.answer_template.why,
                "how": conspiracy_mystery.answer_template.how,
                "combined_hash": conspiracy_mystery.answer_template.combined_hash
            },
            "questions": conspiracy_mystery.questions,
            "subgraphs": [],
            "characters": conspiracy_mystery.characters,
            "crypto_keys": []
        }
        
        # Add subgraph information (evidence chains)
        for sg in conspiracy_mystery.subgraphs:
            subgraph_info = {
                "subgraph_id": sg.subgraph_id,
                "type": sg.subgraph_type.value,
                "contributes_to": sg.contributes_to.value if sg.contributes_to else None,
                "is_red_herring": sg.is_red_herring,
                "evidence_nodes": [
                    node.to_dict() if hasattr(node, 'to_dict') else {
                        "node_id": node.node_id,
                        "evidence_type": node.evidence_type.value if hasattr(node.evidence_type, 'value') else str(node.evidence_type),
                        "content": node.content
                    }
                    for node in sg.evidence_nodes
                ],
                "inference_nodes": [
                    inf.to_dict() if hasattr(inf, 'to_dict') else {
                        "node_id": inf.node_id,
                        "reasoning_type": inf.reasoning_type,
                        "parent_node_ids": inf.parent_node_ids,
                        "required_document_ids": inf.required_document_ids,
                        "inference": inf.inference
                    }
                    for inf in sg.inference_nodes
                ]
            }
            proof_tree["subgraphs"].append(subgraph_info)
        
        # Add crypto keys
        for key in conspiracy_mystery.crypto_keys:
            proof_tree["crypto_keys"].append(
                key.to_dict() if hasattr(key, 'to_dict') else {
                    "key_id": key.key_id,
                    "key_value": getattr(key, 'key_value', None),
                    "inference_description": getattr(key, 'inference_description', None)
                }
            )
        
        return proof_tree
    
    @staticmethod
    def create_answer_hash(who: str, what: str, why: str, how: str) -> str:
        """
        Create the answer hash exactly as the smart contract expects.
        
        Args:
            who: WHO answer
            what: WHAT answer
            why: WHY answer
            how: HOW answer
        
        Returns:
            Hex string of keccak256 hash
        """
        # Lowercase and combine with pipe delimiter (matches smart contract)
        combined = f"{who.lower()}|{what.lower()}|{why.lower()}|{how.lower()}"
        
        # Use keccak256 (same as Solidity's keccak256)
        from eth_utils import keccak
        hash_bytes = keccak(text=combined)
        
        return "0x" + hash_bytes.hex()

