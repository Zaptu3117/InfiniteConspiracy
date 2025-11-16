"""Test script for conspiracy mystery foundation."""

import asyncio
import logging
import sys
import os

# Add src to path (go up to backend, then into src)
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from narrative.conspiracy import (
    PoliticalContextGenerator,
    ConspiracyGenerator,
    SubGraphGenerator
)
from utils import CerebrasClient
from models.conspiracy import ConspiracyPremise


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


async def test_conspiracy_foundation():
    """Test the conspiracy foundation components."""
    
    logger.info("="*60)
    logger.info("TESTING CONSPIRACY MYSTERY FOUNDATION")
    logger.info("="*60)
    logger.info("")
    
    # Initialize LLM client
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        logger.error("❌ CEREBRAS_API_KEY not found in environment")
        return
    
    llm = CerebrasClient(api_key)
    
    # Test 1: Political Context Generation
    logger.info("TEST 1: Political Context Generation")
    logger.info("-" * 60)
    
    context_gen = PoliticalContextGenerator(llm)
    political_context = await context_gen.generate_political_context(
        conspiracy_type="occult",
        difficulty=7
    )
    
    logger.info(f"✅ Political context generated:")
    logger.info(f"   World: {political_context.world_name}")
    logger.info(f"   Shadow agencies: {len(political_context.shadow_agencies)}")
    logger.info(f"   Occult orgs: {len(political_context.occult_organizations)}")
    logger.info(f"   Public narrative: {political_context.public_narrative[:100]}...")
    logger.info("")
    
    # Test 2: Conspiracy Premise Generation
    logger.info("TEST 2: Conspiracy Premise Generation")
    logger.info("-" * 60)
    
    conspiracy_gen = ConspiracyGenerator(llm)
    premise = await conspiracy_gen.generate_conspiracy(
        political_context=political_context,
        difficulty=7,
        conspiracy_type="occult"
    )
    
    logger.info(f"✅ Conspiracy premise generated:")
    logger.info(f"   Name: {premise.conspiracy_name}")
    logger.info(f"   WHO: {premise.who}")
    logger.info(f"   WHAT: {premise.what}")
    logger.info(f"   WHY: {premise.why}")
    logger.info(f"   HOW: {premise.how}")
    logger.info("")
    
    # Test 3: Sub-Graph Generation
    logger.info("TEST 3: Sub-Graph Generation")
    logger.info("-" * 60)
    
    subgraph_gen = SubGraphGenerator()
    subgraphs = subgraph_gen.generate_subgraphs(
        premise=premise,
        political_context=political_context,
        difficulty=7,
        num_documents=20
    )
    
    logger.info(f"✅ Sub-graphs generated: {len(subgraphs)}")
    
    # Show breakdown
    identity_count = sum(1 for sg in subgraphs if sg.subgraph_type.value == "identity")
    psychological_count = sum(1 for sg in subgraphs if sg.subgraph_type.value == "psychological")
    crypto_count = sum(1 for sg in subgraphs if sg.subgraph_type.value == "cryptographic")
    red_herring_count = sum(1 for sg in subgraphs if sg.is_red_herring)
    
    logger.info(f"   Identity chains: {identity_count}")
    logger.info(f"   Psychological chains: {psychological_count}")
    logger.info(f"   Cryptographic chains: {crypto_count}")
    logger.info(f"   Red herrings: {red_herring_count}")
    logger.info("")
    
    # Show sample sub-graphs
    logger.info("Sample Sub-Graphs:")
    for sg in subgraphs[:3]:
        logger.info(f"   - {sg.subgraph_id}: {sg.subgraph_type.value} "
                   f"({'RED HERRING' if sg.is_red_herring else 'VALID'}) "
                   f"→ {sg.contributes_to.value if sg.contributes_to else 'None'}")
        logger.info(f"      Conclusion: {sg.conclusion[:80]}...")
    
    logger.info("")
    logger.info("="*60)
    logger.info("✅ ALL FOUNDATION TESTS PASSED")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(test_conspiracy_foundation())

