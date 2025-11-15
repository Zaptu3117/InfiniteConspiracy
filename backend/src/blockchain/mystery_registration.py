"""Mystery registration on smart contract."""

import logging
from typing import Dict, Any
from web3 import Web3

from .web3_client import Web3Client
from models import Mystery


logger = logging.getLogger(__name__)


class MysteryRegistrar:
    """Register mysteries on the smart contract."""
    
    def __init__(self, web3_client: Web3Client):
        self.client = web3_client
    
    async def register_mystery(
        self,
        mystery: Mystery,
        initial_bounty_ksm: float = 10.0
    ) -> Dict[str, Any]:
        """
        Register a mystery on the blockchain.
        
        Args:
            mystery: Mystery object with hashes generated
            initial_bounty_ksm: Initial bounty in KSM
        
        Returns:
            Transaction details
        """
        logger.info(f"📝 Registering mystery {mystery.metadata.mystery_id} on-chain...")
        
        # Ensure hashes are generated
        if not mystery.answer_hash or not mystery.proof_hash:
            mystery.generate_hashes()
        
        # Convert mystery_id to bytes32
        mystery_id_bytes = self.client.string_to_bytes32(mystery.metadata.mystery_id)
        
        # Convert hashes to bytes32 (remove 0x prefix)
        answer_hash_bytes = bytes.fromhex(mystery.answer_hash[2:])
        proof_hash_bytes = bytes.fromhex(mystery.proof_hash[2:])
        
        # Convert bounty to wei (1 KSM = 10^18 wei)
        bounty_wei = Web3.to_wei(initial_bounty_ksm, 'ether')
        
        logger.info(f"  Mystery ID (bytes32): {mystery_id_bytes.hex()}")
        logger.info(f"  Answer Hash: {mystery.answer_hash}")
        logger.info(f"  Proof Hash: {mystery.proof_hash}")
        logger.info(f"  Difficulty: {mystery.metadata.difficulty}")
        logger.info(f"  Duration: {mystery.metadata.expires_in} seconds")
        logger.info(f"  Initial Bounty: {initial_bounty_ksm} KSM")
        
        try:
            # Call createMystery function
            function_call = self.client.contract.functions.createMystery(
                mystery_id_bytes,
                answer_hash_bytes,
                proof_hash_bytes,
                mystery.metadata.expires_in,
                mystery.metadata.difficulty
            )
            
            # Send transaction
            receipt = await self.client.send_transaction(
                function_call,
                value=bounty_wei
            )
            
            logger.info(f"✅ Mystery registered!")
            logger.info(f"   Tx Hash: {receipt['tx_hash']}")
            logger.info(f"   Block: {receipt['block_number']}")
            logger.info(f"   Gas Used: {receipt['gas_used']}")
            
            return {
                "success": True,
                "mystery_id": mystery.metadata.mystery_id,
                "mystery_id_bytes32": mystery_id_bytes.hex(),
                "tx_hash": receipt['tx_hash'],
                "block_number": receipt['block_number']
            }
        
        except Exception as e:
            logger.error(f"❌ Registration failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_mystery_on_chain(self, mystery_id: str) -> Dict[str, Any]:
        """
        Get mystery data from blockchain.
        
        Args:
            mystery_id: Mystery ID string
        
        Returns:
            Mystery data from contract
        """
        mystery_id_bytes = self.client.string_to_bytes32(mystery_id)
        
        try:
            mystery_data = self.client.contract.functions.getMystery(
                mystery_id_bytes
            ).call()
            
            # Parse tuple into dict
            return {
                "mystery_id": mystery_data[0].hex(),
                "answer_hash": mystery_data[1].hex(),
                "proof_hash": mystery_data[2].hex(),
                "bounty_pool": mystery_data[3],
                "created_at": mystery_data[4],
                "expires_at": mystery_data[5],
                "difficulty": mystery_data[6],
                "solved": mystery_data[7],
                "solver": mystery_data[8],
                "proof_revealed": mystery_data[9],
                "proof_data": mystery_data[10]
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to get mystery: {str(e)}")
            return None

