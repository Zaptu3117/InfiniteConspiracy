#!/usr/bin/env python3
"""Test Replicate image generation."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger
from images import ImageGenerator


async def test_image_generation():
    """Test Replicate image generation."""
    config = load_config()
    logger = setup_logger("test_replicate", "INFO", config.log_dir)
    
    logger.info("="*60)
    logger.info("Testing Replicate Image Generation")
    logger.info("="*60)
    
    if not config.replicate_api_token:
        logger.error("❌ REPLICATE_API_TOKEN not set")
        return False
    
    try:
        generator = ImageGenerator(
            api_token=config.replicate_api_token,
            model="black-forest-labs/flux-schnell"
        )
        
        # Test image generation
        logger.info("\nTest: Generating image...")
        logger.info("Prompt: 'A mysterious detective examining a document'")
        
        output_dir = config.outputs_dir / "test_images"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # generate_image returns a dict with 'path' key
        result = await generator.generate_image(
            prompt="A mysterious detective examining a document",
            image_id="test_detective",
            output_dir=output_dir
        )
        
        if result and result.get("path"):
            from pathlib import Path
            image_path = Path(result["path"])
            logger.info(f"✅ Image generated: {image_path}")
            logger.info(f"   Size: {image_path.stat().st_size / 1024:.2f} KB")
            logger.info("\n✅ Replicate test passed!")
            return True
        else:
            logger.error("❌ Image generation failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Replicate test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Run Replicate tests."""
    print("🧪 Replicate Image Generation Test Suite")
    print("="*60)
    print("⚠️  This test will use your Replicate API credits")
    print("="*60)
    
    passed = await test_image_generation()
    
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Replicate: {'✅ PASS' if passed else '❌ FAIL'}")
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

