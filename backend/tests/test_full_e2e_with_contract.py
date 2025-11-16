"""
Complete End-to-End Test: Generate → Deploy Contract → Register On-Chain → Upload to Arkiv → Verify

This test demonstrates the full pipeline:
1. Deploy smart contract (optional, if not already deployed)
2. Generate conspiracy mystery
3. Convert to blockchain format
4. Register on smart contract
5. Upload documents to Arkiv
6. Verify on-chain and Arkiv data

Usage:
    # With existing contract
    python test_full_e2e_with_contract.py --contract 0xYourContractAddress

    # Deploy new contract first
    python test_full_e2e_with_contract.py --deploy --network hardhat
"""

import asyncio
import logging
import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from dotenv import load_dotenv
load_dotenv()

backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from narrative.conspiracy import ConspiracyPipeline
from utils import CerebrasClient
from arkiv_integration import ArkivClient
from blockchain import Web3Client, MysteryRegistrar, ConspiracyToMysteryConverter

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def deploy_contract_via_hardhat(network: str = "hardhat") -> Optional[Dict[str, Any]]:
    """
    Deploy smart contract using Hardhat.
    
    Args:
        network: "hardhat" for local, "kusama" or "paseo" for testnets
    
    Returns:
        Deployment info dict or None if failed
    """
    logger.info("="*60)
    logger.info("🚀 DEPLOYING SMART CONTRACT")
    logger.info("="*60)
    logger.info(f"   Network: {network}")
    logger.info("")
    
    contracts_dir = Path(__file__).parent.parent / "contracts"
    
    try:
        # Run hardhat deploy script
        cmd = ["npx", "hardhat", "run", "scripts/deploy.js"]
        if network != "hardhat":
            cmd.extend(["--network", network])
        
        logger.info(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=contracts_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            logger.error(f"❌ Deployment failed:")
            logger.error(result.stderr)
            return None
        
        logger.info(result.stdout)
        
        # Read deployment info
        deployment_file = contracts_dir / "deployment.json"
        if not deployment_file.exists():
            logger.error("❌ deployment.json not found")
            return None
        
        with open(deployment_file, 'r') as f:
            deployment_info = json.load(f)
        
        logger.info("")
        logger.info("✅ CONTRACT DEPLOYED")
        logger.info(f"   Address: {deployment_info['contract']}")
        logger.info(f"   Oracle: {deployment_info['oracle']}")
        logger.info(f"   Network: {deployment_info['network']}")
        logger.info("")
        
        return deployment_info
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Deployment timed out")
        return None
    except Exception as e:
        logger.error(f"❌ Deployment error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def full_e2e_test(
    contract_address: Optional[str] = None,
    deploy_contract: bool = False,
    network: str = "hardhat",
    environment: str = "dev",
    difficulty: int = 5,
    num_documents: int = 10,
    conspiracy_type: str = "occult"
):
    """
    Complete end-to-end test.
    
    Args:
        contract_address: Existing contract address (if not deploying)
        deploy_contract: Whether to deploy a new contract
        network: Network for deployment (hardhat/kusama/paseo)
        environment: Environment tag for Arkiv (dev/prod)
        difficulty: Mystery difficulty (1-10)
        num_documents: Number of documents
        conspiracy_type: Type of conspiracy
    """
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*10 + "FULL E2E TEST WITH BLOCKCHAIN" + " "*18 + "║")
    logger.info("╚" + "="*58 + "╝")
    logger.info("")
    
    # ========================================
    # STEP 1: DEPLOY CONTRACT (if requested)
    # ========================================
    if deploy_contract:
        deployment_info = await deploy_contract_via_hardhat(network)
        if not deployment_info:
            logger.error("❌ Contract deployment failed")
            return None
        contract_address = deployment_info['contract']
    else:
        if not contract_address:
            contract_address = os.getenv("CONTRACT_ADDRESS")
        
        if not contract_address:
            logger.error("❌ No contract address provided and CONTRACT_ADDRESS not set")
            logger.info("   Either use --deploy or set CONTRACT_ADDRESS in .env")
            return None
        
        logger.info(f"📜 Using existing contract: {contract_address}")
        logger.info("")
    
    # ========================================
    # STEP 2: GENERATE CONSPIRACY
    # ========================================
    logger.info("="*60)
    logger.info("STEP 2: GENERATING CONSPIRACY MYSTERY")
    logger.info("="*60)
    logger.info("")
    
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    if not cerebras_key:
        logger.error("❌ CEREBRAS_API_KEY required")
        return None
    
    llm = CerebrasClient(cerebras_key)
    config = {
        "political_context": {"temperature": 0.8, "max_tokens": 8000},
        "conspiracy": {"temperature": 0.8, "max_tokens": 8000},
        "psychological": {"temperature": 0.7, "max_tokens": 8000},
        "cryptographic": {"temperature": 0.7, "max_tokens": 8000},
        "document_generation": {"temperature": 0.7, "max_tokens": 8000, "parallel_batch_size": 5},
        "character_enhancement": {"temperature": 0.7, "max_tokens": 8000},
        "num_images": 2
    }
    
    pipeline = ConspiracyPipeline(llm, config, replicate_token=os.getenv("REPLICATE_API_TOKEN"))
    
    try:
        start_time = datetime.now()
        
        conspiracy_mystery = await pipeline.generate_conspiracy_mystery(
            difficulty=difficulty,
            num_documents=num_documents,
            conspiracy_type=conspiracy_type
        )
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        logger.info("")
        logger.info("✅ GENERATION COMPLETE")
        logger.info(f"   Time: {generation_time:.1f}s")
        logger.info(f"   Mystery: {conspiracy_mystery.premise.conspiracy_name}")
        logger.info(f"   World: {conspiracy_mystery.political_context.world_name}")
        logger.info(f"   Documents: {len(conspiracy_mystery.documents)}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 3: CONVERT TO BLOCKCHAIN FORMAT
    # ========================================
    logger.info("="*60)
    logger.info("STEP 3: CONVERTING TO BLOCKCHAIN FORMAT")
    logger.info("="*60)
    logger.info("")
    
    try:
        converter = ConspiracyToMysteryConverter()
        mystery = converter.convert(conspiracy_mystery)
        
        logger.info("✅ CONVERSION COMPLETE")
        logger.info(f"   Answer Hash: {mystery.answer_hash}")
        logger.info(f"   Proof Hash: {mystery.proof_hash}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 4: REGISTER ON BLOCKCHAIN
    # ========================================
    logger.info("="*60)
    logger.info("STEP 4: REGISTERING ON BLOCKCHAIN")
    logger.info("="*60)
    logger.info("")
    
    oracle_key = os.getenv("ORACLE_PRIVATE_KEY") or os.getenv("DEPLOYER_PRIVATE_KEY")
    if not oracle_key:
        logger.error("❌ ORACLE_PRIVATE_KEY or DEPLOYER_PRIVATE_KEY required")
        return None
    
    rpc_url = os.getenv("KUSAMA_RPC_URL", "http://localhost:8545")
    if network == "hardhat":
        rpc_url = "http://localhost:8545"
    
    logger.info(f"   RPC: {rpc_url}")
    logger.info(f"   Contract: {contract_address}")
    
    try:
        web3_client = Web3Client(
            rpc_url=rpc_url,
            private_key=oracle_key,
            contract_address=contract_address
        )
        
        if not await web3_client.is_connected():
            logger.error("❌ Failed to connect to blockchain")
            logger.info("   If using hardhat network, start it first:")
            logger.info("   cd contracts && npx hardhat node")
            return None
        
        logger.info(f"   ✅ Connected")
        logger.info(f"   Oracle: {web3_client.address}")
        
        balance = await web3_client.get_balance()
        logger.info(f"   Balance: {balance / 10**18:.4f} KSM")
        logger.info("")
        
        registrar = MysteryRegistrar(web3_client)
        
        register_start = datetime.now()
        result = await registrar.register_mystery(mystery, initial_bounty_ksm=10.0)
        register_time = (datetime.now() - register_start).total_seconds()
        
        if not result['success']:
            logger.error(f"❌ Registration failed: {result.get('error')}")
            return None
        
        logger.info("")
        logger.info("✅ BLOCKCHAIN REGISTRATION COMPLETE")
        logger.info(f"   Time: {register_time:.1f}s")
        logger.info(f"   Tx Hash: {result['tx_hash']}")
        logger.info(f"   Block: {result['block_number']}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Blockchain registration failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # ========================================
    # STEP 5: UPLOAD TO ARKIV
    # ========================================
    arkiv_key = os.getenv("ARKIV_PRIVATE_KEY")
    if not arkiv_key:
        logger.warning("⚠️  ARKIV_PRIVATE_KEY not set, skipping Arkiv upload")
        upload_to_arkiv = False
    else:
        upload_to_arkiv = True
    
    if upload_to_arkiv:
        logger.info("="*60)
        logger.info("STEP 5: UPLOADING TO ARKIV")
        logger.info("="*60)
        logger.info("")
        
        try:
            async with ArkivClient(
                private_key=arkiv_key,
                rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
                ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
            ) as client:
                
                entities = []
                
                # 1. CONSPIRACY METADATA
                metadata = {
                    "mystery_id": conspiracy_mystery.mystery_id,
                    "conspiracy_name": conspiracy_mystery.premise.conspiracy_name,
                    "world": conspiracy_mystery.political_context.world_name,
                    "difficulty": conspiracy_mystery.difficulty,
                    "total_documents": len(conspiracy_mystery.documents),
                    "created_at": conspiracy_mystery.created_at,
                    "environment": environment,
                    "contract_address": contract_address,
                    "answer_hash": mystery.answer_hash,
                    "proof_hash": mystery.proof_hash
                }
                
                entities.append({
                    "payload": json.dumps(metadata).encode('utf-8'),
                    "content_type": "application/json",
                    "attributes": {
                        "resource_type": "conspiracy",
                        "mystery_id": conspiracy_mystery.mystery_id,
                        "world": conspiracy_mystery.political_context.world_name,
                        "difficulty": str(conspiracy_mystery.difficulty),
                        "conspiracy_type": conspiracy_mystery.premise.conspiracy_type,
                        "environment": environment,
                        "contract_address": contract_address,
                        "status": "active"
                    },
                    "expires_in": 604800
                })
                
                # 2. DOCUMENTS
                for doc in conspiracy_mystery.documents:
                    entities.append({
                        "payload": json.dumps(doc).encode('utf-8'),
                        "content_type": "application/json",
                        "attributes": {
                            "resource_type": "document",
                            "mystery_id": conspiracy_mystery.mystery_id,
                            "document_id": doc.get("document_id"),
                            "doc_type": doc.get("document_type"),
                            "world": conspiracy_mystery.political_context.world_name,
                            "environment": environment
                        },
                        "expires_in": 604800
                    })
                
                # Push in batches
                logger.info(f"   Pushing {len(entities)} entities...")
                batch_size = 10
                total_pushed = 0
                
                upload_start = datetime.now()
                
                for i in range(0, len(entities), batch_size):
                    batch = entities[i:i+batch_size]
                    keys = await client.create_entities_batch(batch)
                    total_pushed += len(keys)
                    logger.info(f"      Batch {i//batch_size + 1}: {len(keys)} entities")
                
                upload_time = (datetime.now() - upload_start).total_seconds()
                
                logger.info("")
                logger.info("✅ ARKIV UPLOAD COMPLETE")
                logger.info(f"   Time: {upload_time:.1f}s")
                logger.info(f"   Total entities: {total_pushed}")
                logger.info("")
        
        except Exception as e:
            logger.error(f"❌ Arkiv upload failed: {e}")
            import traceback
            traceback.print_exc()
    
    # ========================================
    # STEP 6: VERIFY EVERYTHING
    # ========================================
    logger.info("="*60)
    logger.info("STEP 6: VERIFICATION")
    logger.info("="*60)
    logger.info("")
    
    # Verify on-chain
    logger.info("🔍 Verifying blockchain data...")
    on_chain_data = await registrar.get_mystery_on_chain(mystery.metadata.mystery_id)
    
    if on_chain_data:
        logger.info("   ✅ Mystery found on-chain")
        logger.info(f"   Difficulty: {on_chain_data['difficulty']}")
        logger.info(f"   Bounty Pool: {on_chain_data['bounty_pool'] / 10**18} KSM")
        logger.info(f"   Solved: {on_chain_data['solved']}")
    else:
        logger.error("   ❌ Mystery not found on-chain")
    
    logger.info("")
    
    # Verify Arkiv
    if upload_to_arkiv:
        logger.info("🔍 Verifying Arkiv data...")
        try:
            async with ArkivClient(
                private_key=arkiv_key,
                rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
                ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
            ) as client:
                query_string = f'mystery_id = "{conspiracy_mystery.mystery_id}"'
                entities = await client.query_entities(query_string, limit=100)
                
                logger.info(f"   ✅ Found {len(entities)} entities on Arkiv")
                logger.info("")
        except Exception as e:
            logger.error(f"   ❌ Arkiv verification failed: {e}")
    
    # ========================================
    # FINAL SUMMARY
    # ========================================
    logger.info("="*60)
    logger.info("✅ FULL E2E TEST COMPLETE")
    logger.info("="*60)
    logger.info("")
    logger.info("Summary:")
    logger.info(f"  Mystery: {conspiracy_mystery.premise.conspiracy_name}")
    logger.info(f"  Mystery ID: {conspiracy_mystery.mystery_id}")
    logger.info(f"  Contract: {contract_address}")
    logger.info(f"  Environment: {environment}")
    logger.info(f"  World: {conspiracy_mystery.political_context.world_name}")
    logger.info(f"  Difficulty: {conspiracy_mystery.difficulty}/10")
    logger.info(f"  Documents: {len(conspiracy_mystery.documents)}")
    logger.info(f"  Generation time: {generation_time:.1f}s")
    if 'register_time' in locals():
        logger.info(f"  Registration time: {register_time:.1f}s")
    if upload_to_arkiv and 'upload_time' in locals():
        logger.info(f"  Upload time: {upload_time:.1f}s")
    logger.info("")
    logger.info("Answer (for testing):")
    logger.info(f"  WHO: {conspiracy_mystery.answer_template.who}")
    logger.info(f"  WHAT: {conspiracy_mystery.answer_template.what}")
    logger.info(f"  WHY: {conspiracy_mystery.answer_template.why}")
    logger.info(f"  HOW: {conspiracy_mystery.answer_template.how}")
    logger.info("")
    logger.info("Smart Contract Submission Format:")
    logger.info(f'  submitAnswer("{conspiracy_mystery.mystery_id[:16]}...", ')
    logger.info(f'    who="{conspiracy_mystery.answer_template.who[:30]}...",')
    logger.info(f'    what="{conspiracy_mystery.answer_template.what[:30]}...",')
    logger.info(f'    why="{conspiracy_mystery.answer_template.why[:30]}...",')
    logger.info(f'    how="{conspiracy_mystery.answer_template.how[:30]}...")')
    logger.info("")
    
    return {
        "mystery_id": conspiracy_mystery.mystery_id,
        "contract_address": contract_address,
        "answer_hash": mystery.answer_hash,
        "proof_hash": mystery.proof_hash,
        "generation_time": generation_time,
        "success": True
    }


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Full E2E Test with Smart Contract')
    parser.add_argument('--deploy', action='store_true', help='Deploy new contract')
    parser.add_argument('--contract', type=str, help='Existing contract address')
    parser.add_argument('--network', choices=['hardhat', 'kusama', 'paseo'], default='hardhat', help='Network')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev', help='Environment tag')
    parser.add_argument('--difficulty', type=int, default=5, choices=range(1, 11), help='Difficulty (1-10)')
    parser.add_argument('--docs', type=int, default=10, help='Number of documents')
    parser.add_argument('--type', type=str, default='occult', help='Conspiracy type (any narrative seed: reptilians, flat_earth, templar, etc.)')
    
    args = parser.parse_args()
    
    result = await full_e2e_test(
        contract_address=args.contract,
        deploy_contract=args.deploy,
        network=args.network,
        environment=args.env,
        difficulty=args.difficulty,
        num_documents=args.docs,
        conspiracy_type=args.type
    )
    
    if result and result.get('success'):
        logger.info("🎉 Full E2E test passed!")
        return 0
    else:
        logger.error("❌ Full E2E test failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

