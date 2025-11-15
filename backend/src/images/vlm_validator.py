"""VLM (Vision Language Model) validation for generated images."""

import logging
from typing import List, Dict, Any
from utils import OpenAIClient


logger = logging.getLogger(__name__)


class VLMValidator:
    """Validate images contain required visual elements using GPT-4V."""
    
    def __init__(self, openai_client: OpenAIClient):
        self.vlm = openai_client
    
    async def validate_image(
        self,
        image_url: str,
        required_elements: List[str],
        confidence_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Validate that an image contains all required visual elements.
        
        Args:
            image_url: URL or base64 of the image
            required_elements: List of elements that must be present
            confidence_threshold: Minimum confidence required
        
        Returns:
            Validation result with per-element confidence
        """
        logger.info(f"🔍 Validating image...")
        logger.info(f"   Required elements: {required_elements}")
        
        try:
            result = await self.vlm.validate_image(
                image_url,
                required_elements
            )
            
            # Check if all elements present with sufficient confidence
            all_present = result.get("all_present", False)
            overall_confidence = result.get("overall_confidence", 0.0)
            
            passed = all_present and overall_confidence >= confidence_threshold
            
            if passed:
                logger.info(f"   ✅ Validation passed (confidence: {overall_confidence:.2f})")
            else:
                logger.warning(f"   ❌ Validation failed (confidence: {overall_confidence:.2f})")
                
                # Log missing elements
                for elem in result.get("elements", []):
                    if not elem["present"]:
                        logger.warning(f"      Missing: {elem['name']}")
            
            return {
                "passed": passed,
                "overall_confidence": overall_confidence,
                "elements": result.get("elements", []),
                "all_present": all_present
            }
        
        except Exception as e:
            logger.error(f"   ❌ Validation error: {e}")
            return {
                "passed": False,
                "overall_confidence": 0.0,
                "elements": [],
                "all_present": False,
                "error": str(e)
            }
    
    async def validate_batch(
        self,
        images: List[Dict[str, Any]],
        confidence_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple images.
        
        Args:
            images: List of {image_url, required_elements} dicts
            confidence_threshold: Minimum confidence required
        
        Returns:
            List of validation results
        """
        logger.info(f"🔍 Validating {len(images)} images...")
        
        results = []
        for img in images:
            result = await self.validate_image(
                img["image_url"],
                img["required_elements"],
                confidence_threshold
            )
            result["image_id"] = img.get("image_id")
            results.append(result)
        
        passed = [r for r in results if r["passed"]]
        failed = [r for r in results if not r["passed"]]
        
        logger.info(f"   ✅ {len(passed)} passed, ❌ {len(failed)} failed")
        
        return results

