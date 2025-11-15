#!/usr/bin/env python3
"""Test LLM clients (Cerebras and OpenAI)."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger, CerebrasClient, OpenAIClient


async def test_cerebras():
    """Test Cerebras client."""
    config = load_config()
    logger = setup_logger("test_cerebras", "INFO", config.log_dir)
    
    logger.info("="*60)
    logger.info("Testing Cerebras LLM Client")
    logger.info("="*60)
    
    if not config.cerebras_api_key:
        logger.error("❌ CEREBRAS_API_KEY not set")
        return False
    
    try:
        client = CerebrasClient(config.cerebras_api_key)
        
        # Test simple generation
        logger.info("Test 1: Simple text generation...")
        response = await client.generate(
            "Say 'Hello from Cerebras!' in exactly 5 words.",
            temperature=0.7,
            max_tokens=100  # Increased from 20 to avoid truncation
        )
        logger.info(f"✅ Response: {response}")
        
        # Test JSON generation
        logger.info("\nTest 2: JSON generation...")
        json_response = await client.generate_json(
            "Generate a JSON object with 'name' and 'age' fields for a fictional character.",
            temperature=0.7,
            max_tokens=200  # Increased from 100
        )
        logger.info(f"✅ JSON: {json_response}")
        
        logger.info("\n✅ All Cerebras tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cerebras test failed: {e}")
        return False


async def test_openai():
    """Test OpenAI client."""
    config = load_config()
    logger = setup_logger("test_openai", "INFO", config.log_dir)
    
    logger.info("="*60)
    logger.info("Testing OpenAI Client")
    logger.info("="*60)
    
    if not config.openai_api_key:
        logger.error("❌ OPENAI_API_KEY not set")
        return False
    
    try:
        client = OpenAIClient(config.openai_api_key)
        
        # Test simple generation
        logger.info("Test 1: Simple text generation...")
        response = await client.generate(
            "Say 'Hello from OpenAI!' in exactly 5 words.",
            model="gpt-4o-mini",  # Use cheaper model for testing
            temperature=0.7,
            max_tokens=20
        )
        logger.info(f"✅ Response: {response}")
        
        logger.info("\n✅ All OpenAI tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ OpenAI test failed: {e}")
        return False


async def main():
    """Run all LLM tests."""
    print("🧪 LLM Clients Test Suite")
    print("="*60)
    
    cerebras_pass = await test_cerebras()
    print()
    openai_pass = await test_openai()
    
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Cerebras: {'✅ PASS' if cerebras_pass else '❌ FAIL'}")
    print(f"OpenAI:   {'✅ PASS' if openai_pass else '❌ FAIL'}")
    
    return 0 if (cerebras_pass and openai_pass) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

