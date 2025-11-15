#!/usr/bin/env python3
"""
Validate that a mystery requires multi-hop reasoning.

Usage:
    python scripts/validate_mystery.py <mystery_id>
"""

import asyncio
import argparse
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger, CerebrasClient
from models import Mystery
from validation.anti_automation import AntiAutomationValidator


async def validate_mystery(mystery_id: str):
    """Validate a mystery."""
    logger = setup_logger("mystery_validator", "INFO", config.log_dir)
    
    # Load mystery
    mystery_dir = config.outputs_dir / "mysteries" / mystery_id
    mystery_file = mystery_dir / "mystery.json"
    
    if not mystery_file.exists():
        logger.error(f"❌ Mystery not found: {mystery_file}")
        return False
    
    logger.info(f"📂 Loading mystery: {mystery_id}")
    
    with open(mystery_file, 'r') as f:
        mystery_data = json.load(f)
    
    mystery = Mystery(**mystery_data)
    
    logger.info("="*60)
    logger.info("🔍 ANTI-AUTOMATION VALIDATION")
    logger.info("="*60)
    logger.info(f"Mystery ID: {mystery.metadata.mystery_id}")
    logger.info(f"Question: {mystery.metadata.question}")
    logger.info(f"Expected Answer: {mystery.answer}")
    logger.info(f"Documents: {len(mystery.documents)}")
    logger.info(f"Proof Tree Hops: {mystery.proof_tree.get('total_hops', 'N/A')}")
    logger.info("")
    
    # Create validator
    cerebras = CerebrasClient(config.cerebras_api_key)
    validator = AntiAutomationValidator(cerebras)
    
    # Run validation
    result = await validator.validate_mystery(mystery)
    
    # Display results
    logger.info("")
    logger.info("="*60)
    logger.info("📊 VALIDATION RESULTS")
    logger.info("="*60)
    logger.info("")
    
    # Test 1: Single-LLM
    logger.info("TEST 1: Single-LLM (should FAIL to find answer)")
    logger.info(f"  Response: {result.single_llm_response}")
    logger.info(f"  Found Answer: {'❌ YES (BAD!)' if result.single_llm_got_answer else '✅ NO (GOOD!)'}")
    logger.info("")
    
    # Test 2: Multi-hop
    logger.info("TEST 2: Multi-Hop Guided Reasoning (should SUCCEED)")
    for step in result.multi_hop_steps:
        status = "✅" if step.matches else "❌"
        logger.info(f"  Step {step.step_number}: {status}")
        logger.info(f"    Q: {step.sub_question}")
        logger.info(f"    A: {step.llm_response}")
        if not step.matches:
            logger.info(f"    Expected: {step.expected_inference}")
    
    logger.info(f"  Reached Answer: {'✅ YES' if result.multi_hop_reached_answer else '❌ NO'}")
    logger.info("")
    
    # Overall result
    logger.info("="*60)
    if result.is_valid:
        logger.info("✅ MYSTERY IS VALID!")
        logger.info("")
        logger.info("✓ Single-LLM cannot solve it (automation-resistant)")
        logger.info("✓ Multi-hop reasoning can solve it (human-solvable)")
        logger.info("")
        logger.info("This mystery requires careful investigation!")
    else:
        logger.error("❌ MYSTERY IS INVALID!")
        logger.error(f"Reason: {result.reason}")
        logger.error("")
        logger.error("The mystery needs to be regenerated.")
    logger.info("="*60)
    
    return result.is_valid


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate a mystery")
    parser.add_argument("mystery_id", help="Mystery ID to validate")
    args = parser.parse_args()
    
    success = asyncio.run(validate_mystery(args.mystery_id))
    return 0 if success else 1


if __name__ == "__main__":
    from utils.config import config
    sys.exit(main())

