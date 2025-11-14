"""Image generation using Replicate API."""

import logging
import asyncio
import httpx
from typing import Dict, Any, List
from pathlib import Path


logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generate images using Replicate API (Flux/SDXL)."""
    
    def __init__(self, api_token: str, model: str = "black-forest-labs/flux-schnell"):
        self.api_token = api_token
        self.model = model
        self.base_url = "https://api.replicate.com/v1"
    
    async def generate_image(
        self,
        prompt: str,
        image_id: str,
        output_dir: Path,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt.
        
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
                # Create prediction
                async with httpx.AsyncClient(timeout=120.0) as client:
                    # Start prediction
                    headers = {
                        "Authorization": f"Token {self.api_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Use Replicate API - model in version field or direct name
                    # Updated for latest Replicate API (no version hash needed)
                    payload = {
                        "version": self.model if "/" not in self.model else None,
                        "input": {
                            "prompt": prompt,
                            "num_outputs": 1,
                            "aspect_ratio": "16:9",
                            "output_format": "png",
                            "go_fast": True  # Use Flux Schnell's fast mode
                        }
                    }
                    
                    # If model is a full name (like "black-forest-labs/flux-schnell"),
                    # use it directly without version
                    if "/" in self.model:
                        payload = {
                            "model": self.model,
                            "input": payload["input"]
                        }
                        del payload["version"]
                    
                    response = await client.post(
                        f"{self.base_url}/predictions",
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code != 201:
                        raise Exception(f"API error: {response.status_code} - {response.text}")
                    
                    prediction = response.json()
                    prediction_id = prediction["id"]
                    
                    logger.info(f"   Prediction started: {prediction_id}")
                    
                    # Poll for completion
                    max_wait = 120  # 2 minutes
                    wait_interval = 2
                    elapsed = 0
                    
                    while elapsed < max_wait:
                        await asyncio.sleep(wait_interval)
                        elapsed += wait_interval
                        
                        status_response = await client.get(
                            f"{self.base_url}/predictions/{prediction_id}",
                            headers=headers
                        )
                        
                        status = status_response.json()
                        
                        if status["status"] == "succeeded":
                            output_url = status["output"][0] if isinstance(status["output"], list) else status["output"]
                            
                            # Download image
                            image_response = await client.get(output_url)
                            image_bytes = image_response.content
                            
                            # Save image
                            output_dir.mkdir(parents=True, exist_ok=True)
                            image_path = output_dir / f"{image_id}.png"
                            
                            with open(image_path, 'wb') as f:
                                f.write(image_bytes)
                            
                            logger.info(f"   ✅ Image generated: {image_path}")
                            
                            return {
                                "image_id": image_id,
                                "path": str(image_path),
                                "url": output_url,
                                "prompt": prompt,
                                "bytes": image_bytes
                            }
                        
                        elif status["status"] == "failed":
                            raise Exception(f"Generation failed: {status.get('error')}")
                    
                    raise Exception("Timeout waiting for image generation")
            
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

