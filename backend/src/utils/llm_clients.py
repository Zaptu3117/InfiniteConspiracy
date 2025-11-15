"""LLM client wrappers for Cerebras and OpenAI."""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
import httpx

logger = logging.getLogger(__name__)

class CerebrasClient:
    """Wrapper for Cerebras API (gpt-oss-120b)."""
    
    def __init__(self, api_key: str, model: str = "gpt-oss-120b"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.cerebras.ai/v1"
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url
        )
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 8000,
        max_retries: int = 5,
        **kwargs
    ) -> str:
        """
        Generate text using Cerebras LLM with retry logic.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts for rate limits
        
        Returns:
            Generated text
        """
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error (429)
                if "429" in error_str or "rate" in error_str.lower() or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + (attempt * 0.5)  # Exponential backoff with jitter
                        logger.warning(f"   ⚠️  Rate limit hit, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})...")
                        await asyncio.sleep(wait_time)
                        continue
                raise Exception(f"Cerebras API error: {error_str}")
    
    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 8000,
        max_retries: int = 5
    ) -> Dict[str, Any]:
        """Generate JSON output with retry logic."""
        import json
        response = await self.generate(prompt, temperature, max_tokens, max_retries)
        
        if not response:
            raise ValueError("Empty response from LLM")
        
        # Extract JSON from response (handle markdown code blocks)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Log the actual response for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to parse JSON. Response preview: {response[:500]}...")
            logger.error(f"JSON error at position {e.pos}: {e.msg}")
            raise ValueError(f"Invalid JSON response: {e.msg}. Try increasing max_tokens or simplifying the prompt.")


class OpenAIClient:
    """Wrapper for OpenAI API (GPT-4, GPT-4V)."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """Generate text using OpenAI models."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def validate_image(
        self,
        image_url: str,
        required_elements: List[str],
        model: str = "gpt-4o"
    ) -> Dict[str, Any]:
        """
        Use GPT-4V to validate image contains required elements.
        
        Args:
            image_url: URL or base64 of image
            required_elements: List of elements that must be present
        
        Returns:
            Validation result with confidence scores
        """
        elements_list = "\n".join(f"- {elem}" for elem in required_elements)
        
        prompt = f"""Analyze this image and verify if it contains ALL of the following elements:

{elements_list}

For each element, determine:
1. Is it present? (yes/no)
2. Confidence (0.0-1.0)
3. Brief description of what you see

Respond in JSON format:
{{
  "elements": [
    {{"name": "element_name", "present": true/false, "confidence": 0.0-1.0, "description": "..."}}
  ],
  "overall_confidence": 0.0-1.0,
  "all_present": true/false
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            import json
            result_text = response.choices[0].message.content
            
            # Extract JSON
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            return json.loads(result_text.strip())
        
        except Exception as e:
            raise Exception(f"Image validation error: {str(e)}")

