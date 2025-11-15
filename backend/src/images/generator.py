"""Image generation using Replicate API."""

import logging
import asyncio
import os
from typing import Dict, Any, List
from pathlib import Path
import replicate


logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generate images using Replicate API (Flux/SDXL)."""
    
    def __init__(self, api_token: str, model: str = "black-forest-labs/flux-schnell"):
        self.api_token = api_token
        self.model = model
        # Set API token for replicate module
        os.environ["REPLICATE_API_TOKEN"] = api_token
    
    async def generate_image(
        self,
        prompt: str,
        image_id: str,
        output_dir: Path,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt using Replicate SDK.
        
        Args:
            prompt: Text description of the image
            image_id: Unique identifier for the image
            output_dir: Directory to save the image
            max_retries: Maximum number of retry attempts
        
        Returns:
            Dictionary with image info and path
        """
        logger.info(f"🖼️  Generating image: {image_id}")
        logger.info(f"   Prompt: {prompt}")
        
        for attempt in range(max_retries):
            try:
                # Use replicate.run() - runs in thread pool for async compatibility
                loop = asyncio.get_event_loop()
                output = await loop.run_in_executor(
                    None,
                    lambda: replicate.run(
                        self.model,
                        input={
                            "prompt": prompt,
                            "aspect_ratio": "16:9",
                            "output_format": "png",
                            "go_fast": True
                        }
                    )
                )
                
                logger.info(f"   ✅ Generation complete")
                
                # Output is a list of FileOutput objects
                if output and len(output) > 0:
                    file_output = output[0]
                    
                    # Read the image bytes
                    image_bytes = file_output.read()
                    
                    # Get URL if available
                    output_url = str(file_output) if hasattr(file_output, 'url') else None
                    
                    # Save image
                    output_dir.mkdir(parents=True, exist_ok=True)
                    image_path = output_dir / f"{image_id}.png"
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    logger.info(f"   ✅ Image saved: {image_path}")
                    
                    return {
                        "image_id": image_id,
                        "path": str(image_path),
                        "url": output_url,
                        "prompt": prompt
                    }
                else:
                    raise Exception("No output from Replicate")
            
            except Exception as e:
                logger.error(f"   ❌ Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Max retries exceeded")
    
    async def generate_batch(
        self,
        image_specs: List[Dict[str, str]],
        output_dir: Path
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images in parallel.
        
        Args:
            image_specs: List of {image_id, prompt} dicts
            output_dir: Directory to save images
        
        Returns:
            List of generated image info
        """
        logger.info(f"🖼️  Generating {len(image_specs)} images...")
        
        tasks = [
            self.generate_image(
                spec["prompt"],
                spec["image_id"],
                output_dir
            )
            for spec in image_specs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        logger.info(f"   ✅ {len(successful)} succeeded, ❌ {len(failed)} failed")
        
        return successful

