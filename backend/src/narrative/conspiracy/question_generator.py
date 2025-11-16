"""Question generator - creates specific questions tailored to each conspiracy."""

import logging
from typing import Dict
from models.conspiracy import ConspiracyPremise, MysteryAnswer

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generate specific, tailored questions for each conspiracy mystery."""
    
    def __init__(self, llm_client):
        """
        Initialize with LLM client.
        
        Args:
            llm_client: LLM client for question generation
        """
        self.llm = llm_client
    
    async def generate_questions(
        self, 
        premise: ConspiracyPremise,
        answer_template: MysteryAnswer
    ) -> Dict[str, str]:
        """
        Generate 4 specific questions tailored to this conspiracy.
        
        Questions should:
        - Be specific to the conspiracy context
        - Make it clear what type of answer is expected (name, phrase, codename, method)
        - Be answerable from documents
        - Guide players to look for exact strings
        
        Args:
            premise: The conspiracy premise with full narrative
            answer_template: The answer template with exact answers
        
        Returns:
            Dict with "who", "what", "why", "how" questions
        """
        logger.info("Generating tailored questions for conspiracy...")
        
        # Build question generation prompt
        prompt = f"""You are creating specific questions for a conspiracy mystery game.

CONSPIRACY CONTEXT:
- Name: {premise.conspiracy_name}
- Primary Conspirator: {answer_template.who}
- Operation Codename: {answer_template.what}
- Key Phrase/Motto: {answer_template.why}
- Primary Method: {answer_template.how}

PREMISE SUMMARY:
WHO: {premise.who[:200]}...
WHAT: {premise.what[:200]}...
WHY: {premise.why[:200]}...
HOW: {premise.how[:200]}...

TASK: Generate 4 specific questions that guide players to discover these answers.

QUESTION GUIDELINES:

1. WHO Question:
   - Ask about the specific character/person (leader, orchestrator, primary conspirator)
   - Make it clear a NAME is expected
   - Examples: "Which character orchestrated the [operation]?", "Who led the [group/ritual]?", "Which agent was the primary conspirator?"

2. WHAT Question:
   - Ask about the operation/project code name
   - Make it clear a CODENAME is expected
   - Examples: "What was the operation code name?", "What codename did conspirators use?", "What was the project called?"

3. WHY Question (tailored to the type of phrase):
   - If it's a motto/phrase: "What phrase did conspirators use as their motto?"
   - If it's a ritual/artifact name: "What ritual/artifact was central to their plan?"
   - If it's a concept: "What key phrase describes their ultimate goal?"
   - Make it clear a PHRASE or NAME is expected

4. HOW Question:
   - Ask about the primary method/tactic/technique
   - Make it clear a METHOD/ACTION is expected
   - Examples: "What method did they use to infiltrate [target]?", "How did they gain access to [system]?", "What tactic was the first phase?"

OUTPUT FORMAT (JSON only):
{{
  "who": "Specific question about the character/person",
  "what": "Specific question about the operation codename",
  "why": "Specific question about the key phrase/motto/ritual",
  "how": "Specific question about the primary method/tactic"
}}

IMPORTANT:
- Questions should be context-specific (use elements from the premise)
- Avoid generic questions like "Who did it?" or "What happened?"
- Guide players to look for exact strings in documents
- Each question should indicate the TYPE of answer expected

Generate the questions now:"""
        
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=0.7,  # Higher for creative question phrasing
                max_tokens=1000  # Sufficient for questions
            )
            
            # Validate response
            if not response or not isinstance(response, dict):
                logger.error("LLM returned invalid response, using fallback questions")
                return self._generate_fallback_questions(premise, answer_template)
            
            # Extract questions with validation
            questions = {
                "who": response.get("who", "").strip(),
                "what": response.get("what", "").strip(),
                "why": response.get("why", "").strip(),
                "how": response.get("how", "").strip()
            }
            
            # Validate each question is present
            for key, question in questions.items():
                if not question or len(question) < 10:
                    logger.warning(f"{key.upper()} question too short, using fallback")
                    fallback_questions = self._generate_fallback_questions(premise, answer_template)
                    questions[key] = fallback_questions[key]
            
            logger.info(f"   WHO: {questions['who']}")
            logger.info(f"   WHAT: {questions['what']}")
            logger.info(f"   WHY: {questions['why']}")
            logger.info(f"   HOW: {questions['how']}")
            
            return questions
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}, using fallback")
            return self._generate_fallback_questions(premise, answer_template)
    
    def _generate_fallback_questions(
        self, 
        premise: ConspiracyPremise,
        answer_template: MysteryAnswer
    ) -> Dict[str, str]:
        """Generate simple fallback questions if LLM fails."""
        logger.warning("Using fallback question templates")
        
        # Extract operation name without prefix for context
        op_name = answer_template.what
        
        return {
            "who": "Which character was the primary conspirator behind this operation?",
            "what": f"What was the operation code name used by the conspirators?",
            "why": "What key phrase or motto did the conspirators use to describe their goal?",
            "how": "What was the primary method or tactic used in the first phase of the operation?"
        }

