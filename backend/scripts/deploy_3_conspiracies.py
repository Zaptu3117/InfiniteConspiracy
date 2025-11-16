#!/usr/bin/env python3
"""
Deploy 3 conspiracies to Local Hardhat + Arkiv
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from narrative.conspiracy.conspiracy_pipeline import ConspiracyPipeline
from blockchain.web3_client import Web3Client
from blockchain.mystery_registration import MysteryRegistrar
from blockchain.conspiracy_converter import ConspiracyToMysteryConverter
from arkiv_integration.client import ArkivClient
from utils import CerebrasClient


async def deploy_conspiracy(
    difficulty: int,
    num_docs: int,
    conspiracy_type: str,
    conspiracy_num: int,
    llm_client
):
    """Generate and deploy a single conspiracy"""
    print(f"\n{'='*60}")
    print(f"CONSPIRACY #{conspiracy_num}")
    print(f"  Difficulty: {difficulty}")
    print(f"  Documents: {num_docs}")
    print(f"  Type: {conspiracy_type}")
    print(f"{'='*60}\n")
    
    # Configure pipeline with 8000 tokens
    config = {
        "political_context": {"temperature": 0.8, "max_tokens": 8000},
        "conspiracy": {"temperature": 0.8, "max_tokens": 8000},
        "psychological": {"temperature": 0.7, "max_tokens": 8000},
        "cryptographic": {"temperature": 0.7, "max_tokens": 8000},
        "document_generation": {"temperature": 0.7, "max_tokens": 8000, "parallel_batch_size": 5},
        "character_enhancement": {"temperature": 0.7, "max_tokens": 8000},
        "num_images": 2
    }
    
    # Generate conspiracy
    print("STEP 1: Generating Conspiracy Mystery...")
    pipeline = ConspiracyPipeline(llm_client, config, replicate_token=os.getenv("REPLICATE_API_TOKEN"))
    
    conspiracy_mystery = await pipeline.generate_conspiracy_mystery(
        difficulty=difficulty,
        num_documents=num_docs,
        conspiracy_type=conspiracy_type
    )
    
    print(f"\n✅ Generated: {conspiracy_mystery.premise.conspiracy_name}")
    print(f"   Mystery ID: {conspiracy_mystery.mystery_id}")
    print(f"   World: {conspiracy_mystery.political_context.world_name}")
    print(f"   Documents: {len(conspiracy_mystery.documents)}")
    
    # Upload to Arkiv
    print(f"\nSTEP 2: Uploading to Arkiv...")
    arkiv_key = os.getenv("ARKIV_PRIVATE_KEY")
    if not arkiv_key:
        raise ValueError("ARKIV_PRIVATE_KEY required in .env")
    
    async with ArkivClient(
        private_key=arkiv_key,
        rpc_url=os.getenv("ARKIV_RPC_URL", "https://mendoza.hoodi.arkiv.network/rpc"),
        ws_url=os.getenv("ARKIV_WS_URL", "wss://mendoza.hoodi.arkiv.network/rpc/ws")
    ) as arkiv_client:
        arkiv_result = await arkiv_client.push_conspiracy_mystery(conspiracy_mystery)
    
    print(f"✅ Uploaded to Arkiv")
    print(f"   Collection URI: {arkiv_result.get('collection_uri', 'N/A')}")
    
    # Convert to blockchain format
    print(f"\nSTEP 3: Converting to Blockchain Format...")
    converter = ConspiracyToMysteryConverter()
    mystery = converter.convert(conspiracy_mystery)
    
    print(f"✅ Converted")
    print(f"   Answer Hash: {mystery.answer_hash.hex()}")
    print(f"   Proof Hash: {mystery.proof_hash.hex()}")
    
    # Register on blockchain
    print(f"\nSTEP 4: Registering on Local Blockchain...")
    web3_client = Web3Client(network="local")
    await web3_client.initialize()
    
    registrar = MysteryRegistrar(web3_client)
    tx_hash = await registrar.register_mystery(mystery, bounty_ksm=10.0)
    
    print(f"✅ Registered on blockchain")
    print(f"   Transaction: {tx_hash.hex()}")
    
    # Verify on-chain
    on_chain = await registrar.get_mystery_on_chain(mystery.mystery_id)
    print(f"✅ Verified on-chain")
    print(f"   Bounty: {on_chain['bounty'] / 10**18:.2f} KSM")
    print(f"   Difficulty: {on_chain['difficulty']}")
    
    return {
        "conspiracy_num": conspiracy_num,
        "mystery_id": str(mystery.mystery_id),
        "title": conspiracy_mystery.premise.conspiracy_name,
        "tx_hash": tx_hash.hex(),
        "arkiv_uri": arkiv_result.get('collection_uri', 'N/A'),
        "difficulty": difficulty,
        "num_docs": num_docs
    }


async def main():
    """Deploy 3 conspiracies"""
    print("""
╔════════════════════════════════════════════════════════════╗
║  DEPLOYING 3 CONSPIRACIES TO LOCAL HARDHAT + ARKIV        ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Initialize LLM client
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    if not cerebras_key:
        print("❌ CEREBRAS_API_KEY required in .env")
        return
    
    llm = CerebrasClient(cerebras_key)
    print(f"✅ LLM client initialized\n")
    
    conspiracies_config = [
        {"difficulty": 5, "num_docs": 8, "type": "occult", "num": 1},
        {"difficulty": 6, "num_docs": 10, "type": "scientific", "num": 2},
        {"difficulty": 7, "num_docs": 12, "type": "political", "num": 3},
    ]
    
    results = []
    
    for config in conspiracies_config:
        try:
            result = await deploy_conspiracy(
                difficulty=config["difficulty"],
                num_docs=config["num_docs"],
                conspiracy_type=config["type"],
                conspiracy_num=config["num"],
                llm_client=llm
            )
            results.append(result)
        except Exception as e:
            print(f"\n❌ Conspiracy #{config['num']} failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        print(f"\nConspiracy #{result['conspiracy_num']}: {result['title']}")
        print(f"  Mystery ID: {result['mystery_id']}")
        print(f"  Difficulty: {result['difficulty']} | Docs: {result['num_docs']}")
        print(f"  Blockchain TX: {result['tx_hash']}")
        print(f"  Arkiv URI: {result['arkiv_uri']}")
    
    print(f"\n✅ Successfully deployed {len(results)}/3 conspiracies!\n")


if __name__ == "__main__":
    asyncio.run(main())

