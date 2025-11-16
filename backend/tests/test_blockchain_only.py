"""
Simple blockchain test with dummy conspiracy data.
Tests: Converter → Registration → Verification

Usage:
    python test_blockchain_only.py --contract 0xYourContractAddress
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from models.conspiracy import ConspiracyMystery, PoliticalContext, ConspiracyPremise, MysteryAnswer, AnswerDimension
from blockchain import Web3Client, MysteryRegistrar, ConspiracyToMysteryConverter

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def create_dummy_conspiracy():
    """Create a minimal dummy conspiracy for testing blockchain integration."""
    
    # Political context
    political_context = PoliticalContext(
        world_name="Test World",
        time_period="Present Day",
        public_narrative="A stable government maintaining order",
        hidden_reality="Shadow forces manipulate events",
        shadow_agencies=[],
        occult_organizations=[],
        competing_factions=[],
        past_events=[]
    )
    
    # Conspiracy premise
    premise = ConspiracyPremise(
        conspiracy_name="Test Operation",
        conspiracy_type="occult",
        who="Director John Doe leads the Shadow Bureau from the underground facility beneath City Hall",
        what="Execute Project Nightfall to activate a global surveillance network using quantum encryption",
        why="Prevent the prophesied Crisis Event by monitoring all communications for signs of the awakening",
        how="Infiltrate telecommunications infrastructure through backdoor access gained during the emergency protocols"
    )
    
    # Answer template (what gets hashed for blockchain)
    answer_template = MysteryAnswer(
        who="Director John Doe",
        what="Project Nightfall",
        why="Prevent Crisis Event",
        how="Infiltrate telecommunications",
        combined_hash="test_hash"
    )
    
    # Questions
    questions = {
        "who": "Who is the primary conspirator?",
        "what": "What is the operation called?",
        "why": "Why are they doing this?",
        "how": "How are they executing the plan?"
    }
    
    # Create minimal conspiracy
    conspiracy = ConspiracyMystery(
        mystery_id="test_mystery_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        political_context=political_context,
        premise=premise,
        answer_template=answer_template,
        questions=questions,
        subgraphs=[],  # Empty for this test
        crypto_keys=[],  # Empty for this test
        document_assignments=[],
        image_clues=[],
        characters=[],
        timeline=[],
        locations=[],
        documents=[
            {
                "document_id": "doc_001",
                "document_type": "memo",
                "fields": {"content": "Test document mentioning Director John Doe and Project Nightfall"}
            }
        ],
        difficulty=5,
        created_at=datetime.now().isoformat()
    )
    
    return conspiracy


async def test_blockchain_only(contract_address: str):
    """
    Test blockchain integration with dummy data.
    
    Steps:
    1. Create dummy conspiracy
    2. Convert to blockchain format
    3. Register on-chain
    4. Verify on-chain
    """
    
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*10 + "BLOCKCHAIN-ONLY TEST (DUMMY DATA)" + " "*14 + "║")
    logger.info("╚" + "="*58 + "╝")
    logger.info("")
    
    # ========================================
    # STEP 1: CREATE DUMMY CONSPIRACY
    # ========================================
    logger.info("="*60)
    logger.info("STEP 1: CREATING DUMMY CONSPIRACY")
    logger.info("="*60)
    logger.info("")
    
    conspiracy = create_dummy_conspiracy()
    
    logger.info(f"✅ Dummy conspiracy created")
    logger.info(f"   Mystery ID: {conspiracy.mystery_id}")
    logger.info(f"   WHO: {conspiracy.answer_template.who}")
    logger.info(f"   WHAT: {conspiracy.answer_template.what}")
    logger.info(f"   WHY: {conspiracy.answer_template.why}")
    logger.info(f"   HOW: {conspiracy.answer_template.how}")
    logger.info("")
    
    # ========================================
    # STEP 2: CONVERT TO BLOCKCHAIN FORMAT
    # ========================================
    logger.info("="*60)
    logger.info("STEP 2: CONVERTING TO BLOCKCHAIN FORMAT")
    logger.info("="*60)
    logger.info("")
    
    try:
        converter = ConspiracyToMysteryConverter()
        mystery = converter.convert(conspiracy)
        
        logger.info("✅ CONVERSION SUCCESSFUL")
        logger.info(f"   Mystery ID: {mystery.metadata.mystery_id}")
        logger.info(f"   Answer: {mystery.answer[:80]}...")
        logger.info(f"   Answer Hash: {mystery.answer_hash}")
        logger.info(f"   Proof Hash: {mystery.proof_hash}")
        logger.info(f"   Difficulty: {mystery.metadata.difficulty}")
        logger.info(f"   Expires In: {mystery.metadata.expires_in}s")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 3: REGISTER ON BLOCKCHAIN
    # ========================================
    logger.info("="*60)
    logger.info("STEP 3: REGISTERING ON BLOCKCHAIN")
    logger.info("="*60)
    logger.info("")
    
    oracle_key = os.getenv("ORACLE_PRIVATE_KEY")
    if not oracle_key:
        logger.error("❌ ORACLE_PRIVATE_KEY required")
        return None
    
    rpc_url = os.getenv("KUSAMA_RPC_URL", "http://localhost:8545")
    
    logger.info(f"   RPC: {rpc_url}")
    logger.info(f"   Contract: {contract_address}")
    logger.info("")
    
    try:
        web3_client = Web3Client(
            rpc_url=rpc_url,
            private_key=oracle_key,
            contract_address=contract_address
        )
        
        connected = await web3_client.is_connected()
        if not connected:
            logger.error("❌ Failed to connect to blockchain")
            logger.info("   Make sure hardhat node is running:")
            logger.info("   cd contracts && npx hardhat node")
            return None
        
        logger.info(f"   ✅ Connected to blockchain")
        logger.info(f"   Oracle Address: {web3_client.address}")
        
        balance = await web3_client.get_balance()
        logger.info(f"   Balance: {balance / 10**18:.4f} KSM")
        logger.info("")
        
        # Register mystery
        registrar = MysteryRegistrar(web3_client)
        
        logger.info("   📝 Registering mystery on-chain...")
        result = await registrar.register_mystery(mystery, initial_bounty_ksm=5.0)
        
        if not result['success']:
            logger.error(f"❌ Registration failed: {result.get('error')}")
            return None
        
        logger.info("")
        logger.info("✅ REGISTRATION SUCCESSFUL")
        logger.info(f"   Tx Hash: {result['tx_hash']}")
        logger.info(f"   Block: {result['block_number']}")
        logger.info(f"   Mystery ID (bytes32): 0x{result['mystery_id_bytes32']}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 4: VERIFY ON-CHAIN
    # ========================================
    logger.info("="*60)
    logger.info("STEP 4: VERIFYING ON-CHAIN DATA")
    logger.info("="*60)
    logger.info("")
    
    try:
        on_chain_data = await registrar.get_mystery_on_chain(mystery.metadata.mystery_id)
        
        if on_chain_data:
            logger.info("✅ MYSTERY FOUND ON-CHAIN")
            logger.info(f"   Difficulty: {on_chain_data['difficulty']}")
            logger.info(f"   Bounty Pool: {on_chain_data['bounty_pool'] / 10**18} KSM")
            logger.info(f"   Created At: {on_chain_data['created_at']}")
            logger.info(f"   Expires At: {on_chain_data['expires_at']}")
            logger.info(f"   Solved: {on_chain_data['solved']}")
            logger.info(f"   Answer Hash: 0x{on_chain_data['answer_hash']}")
            logger.info(f"   Proof Hash: 0x{on_chain_data['proof_hash']}")
        else:
            logger.error("❌ Mystery not found on-chain")
            return None
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    logger.info("")
    logger.info("="*60)
    logger.info("✅ BLOCKCHAIN TEST COMPLETE")
    logger.info("="*60)
    logger.info("")
    logger.info("Summary:")
    logger.info(f"  Mystery ID: {mystery.metadata.mystery_id}")
    logger.info(f"  Contract: {contract_address}")
    logger.info(f"  Tx Hash: {result['tx_hash']}")
    logger.info(f"  Answer Format: WHO|WHAT|WHY|HOW")
    logger.info(f"  Answer Hash: {mystery.answer_hash}")
    logger.info("")
    logger.info("Test Answer (for verification):")
    logger.info(f'  submitAnswer(')
    logger.info(f'    who="{conspiracy.answer_template.who}",')
    logger.info(f'    what="{conspiracy.answer_template.what}",')
    logger.info(f'    why="{conspiracy.answer_template.why}",')
    logger.info(f'    how="{conspiracy.answer_template.how}"')
    logger.info(f'  )')
    logger.info("")
    logger.info("🎉 All blockchain operations working!")
    logger.info("")
    
    return {
        "success": True,
        "mystery_id": mystery.metadata.mystery_id,
        "contract_address": contract_address,
        "tx_hash": result['tx_hash'],
        "answer_hash": mystery.answer_hash
    }


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Blockchain-only test with dummy data')
    parser.add_argument('--contract', type=str, required=True, help='Contract address')
    
    args = parser.parse_args()
    
    result = await test_blockchain_only(args.contract)
    
    if result and result.get('success'):
        logger.info("✅ Blockchain test passed!")
        return 0
    else:
        logger.error("❌ Blockchain test failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

