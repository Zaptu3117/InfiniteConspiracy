"""Proof management for blockchain contract."""

import json
import logging
from typing import Dict, Any

from .web3_client import Web3Client


logger = logging.getLogger(__name__)


class ProofManager:
    """Manage proof revelation on blockchain."""
    
    def __init__(self, web3_client: Web3Client):
        self.client = web3_client
    
    async def reveal_proof(
        self,
        mystery_id: str,
        proof_tree: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reveal proof on blockchain after mystery expires or is solved.
        
        Args:
            mystery_id: Mystery ID string
            proof_tree: Complete proof tree data
        
        Returns:
            Transaction details
        """
        logger.info(f"🔓 Revealing proof for mystery {mystery_id}...")
        
        # Convert mystery_id to bytes32
        mystery_id_bytes = self.client.string_to_bytes32(mystery_id)
        
        # Convert proof tree to JSON string
        proof_json = json.dumps(proof_tree, sort_keys=True)
        
        logger.info(f"  Mystery ID (bytes32): {mystery_id_bytes.hex()}")
        logger.info(f"  Proof size: {len(proof_json)} bytes")
        
        try:
            # Call revealProof function
            function_call = self.client.contract.functions.revealProof(
                mystery_id_bytes,
                proof_json
            )
            
            # Send transaction
            receipt = await self.client.send_transaction(function_call)
            
            logger.info(f"✅ Proof revealed!")
            logger.info(f"   Tx Hash: {receipt['tx_hash']}")
            logger.info(f"   Block: {receipt['block_number']}")
            
            return {
                "success": True,
                "mystery_id": mystery_id,
                "tx_hash": receipt['tx_hash'],
                "block_number": receipt['block_number']
            }
        
        except Exception as e:
            logger.error(f"❌ Proof revelation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

