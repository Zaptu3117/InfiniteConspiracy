"""
Deploy a generated conspiracy to a specific network (Paseo, Kusama, or local).

This script:
1. Loads stored contract address for the network
2. Generates a conspiracy mystery
3. Registers it on the blockchain
4. Uploads documents to Arkiv
5. Verifies everything

Usage:
    # Deploy to Paseo testnet
    python deploy_conspiracy_to_network.py --network paseo --difficulty 5 --docs 8
    
    # Deploy to local hardhat
    python deploy_conspiracy_to_network.py --network local --difficulty 4 --docs 5
    
    # Deploy to Kusama mainnet (requires confirmation)
    python deploy_conspiracy_to_network.py --network kusama --difficulty 7 --docs 15
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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from narrative.conspiracy import ConspiracyPipeline
from utils import CerebrasClient
from arkiv_integration import ArkivClient
from blockchain import Web3Client, MysteryRegistrar, ConspiracyToMysteryConverter

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def load_contract_address(network: str) -> Optional[Dict[str, Any]]:
    """Load contract address for a specific network."""
    addresses_file = Path(__file__).parent / "contract_addresses.json"
    
    if not addresses_file.exists():
        logger.error("❌ contract_addresses.json not found")
        logger.info("   Deploy a contract first:")
        logger.info(f"   python deploy_contract_to_network.py --network {network}")
        return None
    
    with open(addresses_file, 'r') as f:
        addresses = json.load(f)
    
    if network not in addresses:
        logger.error(f"❌ No contract address found for network: {network}")
        logger.info("   Available networks:")
        for net in addresses.keys():
            logger.info(f"      - {net}")
        return None
    
    network_config = addresses[network]
    
    if not network_config.get("address"):
        logger.error(f"❌ Contract not deployed to {network}")
        logger.info(f"   Deploy first: python deploy_contract_to_network.py --network {network}")
        return None
    
    return network_config


async def deploy_conspiracy(
    network: str,
    difficulty: int = 5,
    num_documents: int = 10,
    conspiracy_type: str = "occult",
    environment: str = "dev"
):
    """
    Deploy a conspiracy to a specific network.
    
    Args:
        network: Network to deploy to (local, paseo, kusama)
        difficulty: Mystery difficulty (1-10)
        num_documents: Number of documents
        conspiracy_type: Type of conspiracy
        environment: Environment tag for Arkiv (dev/prod)
    """
    
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + f"  DEPLOY CONSPIRACY TO {network.upper()}" + " "*(38-len(network)) + "║")
    logger.info("╚" + "="*58 + "╝")
    logger.info("")
    
    # Mainnet warning
    if network == "kusama":
        logger.warning("⚠️  DEPLOYING TO KUSAMA MAINNET - Real funds will be used!")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Deployment cancelled.")
            return None
    
    # Load contract address
    logger.info(f"📋 Loading contract address for {network}...")
    contract_config = load_contract_address(network)
    if not contract_config:
        return None
    
    contract_address = contract_config["address"]
    rpc_url = contract_config["rpc_url"]
    
    logger.info(f"   ✅ Contract: {contract_address}")
    logger.info(f"   RPC: {rpc_url}")
    logger.info("")
    
    # Check API keys
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    oracle_key = os.getenv("ORACLE_PRIVATE_KEY")
    arkiv_key = os.getenv("ARKIV_PRIVATE_KEY")
    
    if not cerebras_key:
        logger.error("❌ CEREBRAS_API_KEY required")
        return None
    
    if not oracle_key:
        logger.error("❌ ORACLE_PRIVATE_KEY required")
        return None
    
    # ========================================
    # STEP 1: GENERATE CONSPIRACY
    # ========================================
    logger.info("="*60)
    logger.info("STEP 1: GENERATING CONSPIRACY MYSTERY")
    logger.info("="*60)
    logger.info(f"   Difficulty: {difficulty}/10")
    logger.info(f"   Documents: {num_documents}")
    logger.info(f"   Type: {conspiracy_type}")
    logger.info("")
    
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
    # STEP 2: CONVERT TO BLOCKCHAIN FORMAT
    # ========================================
    logger.info("="*60)
    logger.info("STEP 2: CONVERTING TO BLOCKCHAIN FORMAT")
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
    # STEP 3: REGISTER ON BLOCKCHAIN
    # ========================================
    logger.info("="*60)
    logger.info(f"STEP 3: REGISTERING ON {network.upper()} BLOCKCHAIN")
    logger.info("="*60)
    logger.info("")
    
    bounty = 10.0 if network != "kusama" else 5.0
    register_start = datetime.now()
    
    # Paseo has "Invalid Transaction" issues with web3.py
    # Use Hardhat script instead (works reliably)
    if network == "paseo":
        logger.info("   ⚠️  Using Hardhat for Paseo (web3.py has known issues)")
        logger.info("")
        
        try:
            # Create mystery data JSON for Hardhat script
            mystery_data = {
                "mysteryId": mystery.metadata.mystery_id,
                "answerHash": mystery.answer_hash,
                "proofHash": mystery.proof_hash,
                "duration": mystery.metadata.expires_in,
                "difficulty": mystery.metadata.difficulty,
                "bountyKSM": bounty
            }
            
            temp_file = Path("/tmp/mystery_registration.json")
            with open(temp_file, 'w') as f:
                json.dump(mystery_data, f)
            
            # Run Hardhat script with env variables
            contracts_dir = Path(__file__).parent.parent / "contracts"
            env = os.environ.copy()
            env["MYSTERY_DATA_FILE"] = str(temp_file)
            env["CONTRACT_ADDRESS"] = contract_address
            env["NETWORK_NAME"] = network
            
            cmd = f"npx hardhat run scripts/register_mystery.js --network {network}"
            
            logger.info(f"   🔨 Running: {cmd}")
            logger.info(f"   📁 Working directory: {contracts_dir}")
            logger.info("")
            
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(contracts_dir),
                capture_output=True,
                text=True,
                env=env
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Hardhat registration failed:")
                logger.error(result.stdout)
                logger.error(result.stderr)
                return None
            
            logger.info(result.stdout)
            
            # Parse output for tx hash and block
            tx_hash = None
            block_number = None
            for line in result.stdout.split('\n'):
                if 'Tx Hash:' in line:
                    tx_hash = line.split('Tx Hash:')[1].strip()
                if 'Block:' in line:
                    block_number = line.split('Block:')[1].strip()
            
            register_time = (datetime.now() - register_start).total_seconds()
            
            logger.info("")
            logger.info("✅ BLOCKCHAIN REGISTRATION COMPLETE")
            logger.info(f"   Time: {register_time:.1f}s")
            if tx_hash:
                logger.info(f"   Tx Hash: {tx_hash}")
            if block_number:
                logger.info(f"   Block: {block_number}")
            logger.info(f"   Bounty: {bounty} KSM")
            logger.info("")
            
        except Exception as e:
            logger.error(f"❌ Hardhat registration failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        # Use web3.py for local/other networks
        try:
            web3_client = Web3Client(
                rpc_url=rpc_url,
                private_key=oracle_key,
                contract_address=contract_address
            )
            
            if not await web3_client.is_connected():
                logger.error("❌ Failed to connect to blockchain")
                return None
            
            logger.info(f"   ✅ Connected to {network}")
            logger.info(f"   Oracle: {web3_client.address}")
            
            balance = await web3_client.get_balance()
            logger.info(f"   Balance: {balance / 10**18:.4f} KSM")
            logger.info("")
            
            registrar = MysteryRegistrar(web3_client)
            
            result = await registrar.register_mystery(mystery, initial_bounty_ksm=bounty)
            register_time = (datetime.now() - register_start).total_seconds()
            
            if not result['success']:
                logger.error(f"❌ Registration failed: {result.get('error')}")
                return None
            
            logger.info("")
            logger.info("✅ BLOCKCHAIN REGISTRATION COMPLETE")
            logger.info(f"   Time: {register_time:.1f}s")
            logger.info(f"   Tx Hash: {result['tx_hash']}")
            logger.info(f"   Block: {result['block_number']}")
            logger.info(f"   Bounty: {bounty} KSM")
            logger.info("")
            
        except Exception as e:
            logger.error(f"❌ Blockchain registration failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # ========================================
    # STEP 4: UPLOAD TO ARKIV
    # ========================================
    if not arkiv_key:
        logger.warning("⚠️  ARKIV_PRIVATE_KEY not set, skipping Arkiv upload")
        upload_to_arkiv = False
    else:
        upload_to_arkiv = True
    
    if upload_to_arkiv:
        logger.info("="*60)
        logger.info("STEP 4: UPLOADING TO ARKIV")
        logger.info("="*60)
        logger.info("")
        
        try:
            async with ArkivClient(
                private_key=arkiv_key,
                rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
                ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
            ) as client:
                
                entities = []
                
                # Conspiracy metadata
                metadata = {
                    "mystery_id": conspiracy_mystery.mystery_id,
                    "conspiracy_name": conspiracy_mystery.premise.conspiracy_name,
                    "world": conspiracy_mystery.political_context.world_name,
                    "difficulty": conspiracy_mystery.difficulty,
                    "total_documents": len(conspiracy_mystery.documents),
                    "created_at": conspiracy_mystery.created_at,
                    "environment": environment,
                    "network": network,
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
                        "network": network,
                        "contract_address": contract_address,
                        "status": "active"
                    },
                    "expires_in": 604800
                })
                
                # Documents
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
                            "environment": environment,
                            "network": network
                        },
                        "expires_in": 604800
                    })
                
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
    # FINAL SUMMARY
    # ========================================
    logger.info("="*60)
    logger.info("✅ DEPLOYMENT COMPLETE")
    logger.info("="*60)
    logger.info("")
    logger.info("Summary:")
    logger.info(f"  Mystery: {conspiracy_mystery.premise.conspiracy_name}")
    logger.info(f"  Mystery ID: {conspiracy_mystery.mystery_id}")
    logger.info(f"  Network: {network}")
    logger.info(f"  Contract: {contract_address}")
    logger.info(f"  Tx Hash: {result['tx_hash']}")
    logger.info(f"  Bounty: {bounty} KSM")
    logger.info(f"  Generation time: {generation_time:.1f}s")
    logger.info(f"  Registration time: {register_time:.1f}s")
    if upload_to_arkiv:
        logger.info(f"  Upload time: {upload_time:.1f}s")
    logger.info("")
    logger.info("Answer (for testing):")
    logger.info(f"  WHO: {conspiracy_mystery.answer_template.who}")
    logger.info(f"  WHAT: {conspiracy_mystery.answer_template.what}")
    logger.info(f"  WHY: {conspiracy_mystery.answer_template.why}")
    logger.info(f"  HOW: {conspiracy_mystery.answer_template.how}")
    logger.info("")
    logger.info(f"🎉 Conspiracy deployed to {network}!")
    logger.info("")
    
    return {
        "mystery_id": conspiracy_mystery.mystery_id,
        "contract_address": contract_address,
        "network": network,
        "tx_hash": result['tx_hash'],
        "answer_hash": mystery.answer_hash,
        "proof_hash": mystery.proof_hash,
        "success": True
    }


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy conspiracy to network')
    parser.add_argument(
        '--network',
        choices=['local', 'paseo', 'kusama'],
        required=True,
        help='Network to deploy to'
    )
    parser.add_argument('--difficulty', type=int, default=5, choices=range(1, 11))
    parser.add_argument('--docs', type=int, default=10, help='Number of documents')
    parser.add_argument('--type', choices=['occult', 'secret_society', 'underground_network'], default='occult')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev', help='Environment tag')
    
    args = parser.parse_args()
    
    result = await deploy_conspiracy(
        network=args.network,
        difficulty=args.difficulty,
        num_documents=args.docs,
        conspiracy_type=args.type,
        environment=args.env
    )
    
    if result and result.get('success'):
        logger.info("✅ Deployment successful!")
        return 0
    else:
        logger.error("❌ Deployment failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

