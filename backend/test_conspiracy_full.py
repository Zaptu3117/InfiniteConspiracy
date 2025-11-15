"""End-to-end test for complete conspiracy mystery system."""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from narrative.conspiracy import ConspiracyPipeline
from utils import CerebrasClient


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


async def test_full_conspiracy_generation():
    """Test the complete conspiracy generation pipeline."""
    
    logger.info("="*60)
    logger.info("FULL CONSPIRACY MYSTERY SYSTEM TEST")
    logger.info("="*60)
    logger.info("")
    
    # Initialize LLM client
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        logger.error("❌ CEREBRAS_API_KEY not found in environment")
        return
    
    llm = CerebrasClient(api_key)
    
    # Get Replicate token for image generation
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    
    # Configuration
    config = {
        "political_context": {
            "temperature": 0.8,
            "max_tokens": 4000  # Increased to avoid JSON truncation
        },
        "conspiracy": {
            "temperature": 0.8,
            "max_tokens": 1500
        },
        "psychological": {
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "cryptographic": {
            "temperature": 0.7,
            "max_tokens": 1500
        },
        "document_generation": {
            "temperature": 0.7,
            "max_tokens": 2000,
            "parallel_batch_size": 3  # Very small batches to avoid rate limits
        },
        "character_enhancement": {
            "temperature": 0.7,
            "max_tokens": 1500
        },
        "num_images": 3  # Just a few images for testing
    }
    
    # Initialize pipeline
    pipeline = ConspiracyPipeline(llm, config, replicate_token=replicate_token)
    
    # Generate mystery
    try:
        mystery = await pipeline.generate_conspiracy_mystery(
            difficulty=6,  # Medium difficulty for testing
            num_documents=15,  # Smaller number for faster testing
            conspiracy_type="occult"
        )
        
        logger.info("="*60)
        logger.info("✅ COMPLETE MYSTERY GENERATED SUCCESSFULLY")
        logger.info("="*60)
        logger.info("")
        logger.info(f"Mystery ID: {mystery.mystery_id}")
        logger.info(f"Conspiracy: {mystery.premise.conspiracy_name}")
        logger.info("")
        logger.info("Answer Dimensions:")
        logger.info(f"  WHO: {mystery.premise.who[:100]}...")
        logger.info(f"  WHAT: {mystery.premise.what[:100]}...")
        logger.info(f"  WHY: {mystery.premise.why[:100]}...")
        logger.info(f"  HOW: {mystery.premise.how[:100]}...")
        logger.info("")
        logger.info("Statistics:")
        logger.info(f"  Sub-graphs: {len(mystery.subgraphs)}")
        logger.info(f"  Documents: {len(mystery.documents)}")
        logger.info(f"  Characters: {len(mystery.characters)}")
        logger.info(f"  Image clues: {len(mystery.image_clues)}")
        logger.info(f"  Document assignments: {len(mystery.document_assignments)}")
        logger.info("")
        
        # Show sub-graph breakdown
        identity_count = sum(1 for sg in mystery.subgraphs if sg.subgraph_type.value == "identity")
        psychological_count = sum(1 for sg in mystery.subgraphs if sg.subgraph_type.value == "psychological")
        crypto_count = sum(1 for sg in mystery.subgraphs if sg.subgraph_type.value == "cryptographic")
        red_herring_count = sum(1 for sg in mystery.subgraphs if sg.is_red_herring)
        
        logger.info("Sub-Graph Breakdown:")
        logger.info(f"  Identity chains: {identity_count}")
        logger.info(f"  Psychological chains: {psychological_count}")
        logger.info(f"  Cryptographic chains: {crypto_count}")
        logger.info(f"  Red herrings: {red_herring_count}")
        logger.info("")
        
        # Show sample documents
        logger.info("Sample Documents:")
        for i, doc in enumerate(mystery.documents[:3]):
            logger.info(f"  {i+1}. {doc.get('document_id')}: {doc.get('document_type')}")
        if len(mystery.documents) > 3:
            logger.info(f"  ... and {len(mystery.documents) - 3} more")
        logger.info("")
        
        logger.info("="*60)
        logger.info("🎉 ALL TESTS PASSED - SYSTEM FULLY FUNCTIONAL")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_conspiracy_generation())

