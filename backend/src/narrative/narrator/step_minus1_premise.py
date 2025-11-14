"""Step -1: Mystery Premise Generation - create question and answer with LLM."""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


PREMISE_GENERATION_PROMPT = """You are creating the core question and answer for a detective mystery.

MYSTERY SETTINGS:
- Setting: {setting}
- Time Period: {time_period}
- Difficulty: {difficulty}/10
- Genre: Corporate/Office Mystery

YOUR TASK:
Generate a compelling mystery question and its answer.

REQUIREMENTS:
1. Question should be clear, specific, and intriguing
2. Answer should be a person's name (full name)
3. Question should be answerable through investigation
4. Avoid overly complex or abstract questions
5. Make it suitable for the difficulty level

DIFFICULTY GUIDELINES:
- Low (1-3): Simple "who did X" questions
- Medium (4-7): Requires connecting multiple pieces of evidence
- High (8-10): Complex scenarios with multiple suspects

GOOD EXAMPLES:
- "Who leaked the classified documents to the press?"
- "Who accessed the secure server at 2:47 AM?"
- "Who sabotaged the security system?"
- "Who transferred the funds illegally?"
- "Who stole the research prototype?"

BAD EXAMPLES:
- "What happened?" (too vague)
- "Why did John do it?" (assumes John did it)
- "Where is the money?" (not asking who)

Output ONLY valid JSON:
{{
  "question": "Who...",
  "answer": "Full Name",
  "reasoning": "Brief explanation of why this mystery is interesting"
}}"""


class PremiseGenerator:
    """Generate mystery premise (question + answer) using LLM."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def generate_premise(
        self,
        difficulty: int,
        config: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        Generate mystery question and answer using LLM.
        
        Args:
            difficulty: Mystery difficulty (1-10)
            config: Configuration with setting, time_period, etc.
        
        Returns:
            Tuple of (question, answer)
        """
        logger.info("❓ Step -1: Generating mystery premise...")
        logger.info(f"   Difficulty: {difficulty}/10")
        
        # Get setting details
        setting = config.get("setting", "corporate office")
        time_period = config.get("time_period", "modern day")
        
        # Build prompt
        prompt = PREMISE_GENERATION_PROMPT.format(
            setting=setting,
            time_period=time_period,
            difficulty=difficulty
        )
        
        # Generate with LLM
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.8),  # Higher temp for creativity
                max_tokens=config.get("max_tokens", 500)
            )
            
            question = response.get("question", "")
            answer = response.get("answer", "")
            reasoning = response.get("reasoning", "")
            
            if not question or not answer:
                raise ValueError("LLM failed to generate valid question/answer")
            
            logger.info(f"   ✅ Premise generated")
            logger.info(f"      Question: {question}")
            logger.info(f"      Answer: {answer}")
            logger.info(f"      Reasoning: {reasoning}")
            logger.info("")
            
            return question, answer
        
        except Exception as e:
            logger.error(f"   ❌ Premise generation failed: {e}")
            logger.warning("   ⚠️  Using fallback premise")
            
            # Fallback to simple premise
            return self._generate_fallback_premise(difficulty, setting)
    
    def _generate_fallback_premise(self, difficulty: int, setting: str) -> tuple[str, str]:
        """Generate a fallback premise if LLM fails."""
        import random
        
        # Template questions by difficulty
        easy_questions = [
            "Who accessed the restricted area without authorization?",
            "Who sent the anonymous email to management?",
            "Who leaked the meeting notes?"
        ]
        
        medium_questions = [
            "Who stole the classified documents from the secure vault?",
            "Who sabotaged the security camera system?",
            "Who transferred funds to the offshore account?"
        ]
        
        hard_questions = [
            "Who orchestrated the data breach and framed another employee?",
            "Who coordinated the insider trading scheme?",
            "Who planted false evidence to mislead the investigation?"
        ]
        
        # Select based on difficulty
        if difficulty <= 3:
            question = random.choice(easy_questions)
        elif difficulty <= 7:
            question = random.choice(medium_questions)
        else:
            question = random.choice(hard_questions)
        
        # Generate random name for answer
        first_names = ["Sarah", "Michael", "Jennifer", "David", "Emily", "Robert", "Lisa", "James"]
        last_names = ["Martinez", "Johnson", "Williams", "Brown", "Davis", "Chen", "Garcia", "Miller"]
        
        answer = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        logger.info(f"      Fallback Question: {question}")
        logger.info(f"      Fallback Answer: {answer}")
        logger.info("")
        
        return question, answer

