"""Step 1: Character Generation for narrative."""

import logging
from typing import List, Dict, Any
from ..graph import Character


logger = logging.getLogger(__name__)


CHARACTER_GENERATION_PROMPT = """You are creating characters for a detective mystery story.

MYSTERY CONTEXT:
- Setting: {setting_type}
- Time period: {time_period}
- Difficulty level: {difficulty}/10
- Answer involves: {answer_hint}

PROOF TREE SUMMARY:
The mystery requires connecting these types of evidence:
{proof_tree_types}

YOUR TASK:
Create {num_characters} realistic characters (between 5-10 people) that fit naturally into this mystery.

For each character provide:
- name: Full name (realistic for the setting)
- role: Job/position that's relevant to the mystery context
- background: 2-3 sentence backstory
- personality: Key personality traits (3-5 words)
- relationships: Dictionary mapping other character names to relationship types
  Example: {{"Character Name": "colleague", "Another Name": "rival"}}
- access_level: List of what information/locations they can access
  Example: ["server room", "financial records", "email system"]
- secrets: What they're hiding (if anything) - keep it subtle
- motivation: What drives their actions in 1-2 sentences

IMPORTANT:
- Make characters feel like real people with complex motivations
- Not all characters need to be directly involved in the mystery
- Include some characters who are just part of the world
- Vary roles, backgrounds, and personalities
- Create realistic workplace/social dynamics

Output ONLY valid JSON in this exact format:
{{
  "characters": [
    {{
      "name": "Full Name",
      "role": "Job Title",
      "background": "Brief backstory...",
      "personality": "trait1, trait2, trait3",
      "relationships": {{"Name1": "relationship", "Name2": "relationship"}},
      "access_level": ["access1", "access2"],
      "secrets": "What they hide...",
      "motivation": "What drives them..."
    }}
  ]
}}"""


class CharacterGenerator:
    """Generate characters using LLM."""
    
    def __init__(self, llm_client):
        """
        Initialize character generator.
        
        Args:
            llm_client: LLM client (Cerebras or similar)
        """
        self.llm = llm_client
    
    async def generate_characters(
        self,
        mystery_context: Dict[str, Any],
        proof_tree: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[Character]:
        """
        Generate characters for the mystery.
        
        Args:
            mystery_context: {question, answer, difficulty, setting, time_period}
            proof_tree: Proof tree structure
            config: Configuration including num_characters range
        
        Returns:
            List of Character objects
        """
        logger.info("🎭 Step 1: Generating characters...")
        
        # Determine number of characters
        num_chars_range = config.get("num_characters", [5, 10])
        import random
        num_characters = random.randint(num_chars_range[0], num_chars_range[1])
        
        # Build prompt
        prompt = self._build_prompt(
            mystery_context,
            proof_tree,
            num_characters
        )
        
        # Generate with LLM
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.8),
                max_tokens=config.get("max_tokens", 3000)
            )
            
            # Parse characters
            characters = [
                Character.from_dict(char_data)
                for char_data in response.get("characters", [])
            ]
            
            # Validate
            self._validate_characters(characters)
            
            logger.info(f"   ✅ Generated {len(characters)} characters")
            for char in characters:
                logger.info(f"      - {char.name} ({char.role})")
            
            return characters
        
        except Exception as e:
            logger.error(f"   ❌ Character generation failed: {e}")
            raise
    
    def _build_prompt(
        self,
        mystery_context: Dict[str, Any],
        proof_tree: Dict[str, Any],
        num_characters: int
    ) -> str:
        """Build the character generation prompt."""
        
        # Extract proof tree types
        proof_tree_types = self._extract_proof_tree_types(proof_tree)
        
        # Determine answer hint (without revealing too much)
        answer = mystery_context.get("answer", "")
        answer_hint = self._create_answer_hint(answer)
        
        # Fill prompt template
        prompt = CHARACTER_GENERATION_PROMPT.format(
            setting_type=mystery_context.get("setting", "corporate office"),
            time_period=mystery_context.get("time_period", "modern day"),
            difficulty=mystery_context.get("difficulty", 5),
            answer_hint=answer_hint,
            proof_tree_types=proof_tree_types,
            num_characters=num_characters
        )
        
        return prompt
    
    def _extract_proof_tree_types(self, proof_tree: Dict[str, Any]) -> str:
        """Extract evidence types needed from proof tree."""
        # Get inference nodes
        nodes = proof_tree.get("inference_nodes", [])
        
        if not nodes:
            return "badge access, email communication, financial records, witness statements"
        
        # Extract document types mentioned
        doc_types = set()
        for node in nodes:
            reasoning_type = node.get("reasoning_type", "")
            doc_ids = node.get("document_ids", [])
            
            # Infer evidence types from reasoning
            if "temporal" in reasoning_type:
                doc_types.add("timestamp records")
            if "cross_reference" in reasoning_type:
                doc_types.add("cross-referenced documents")
            if "financial" in str(doc_ids).lower():
                doc_types.add("financial records")
            if "badge" in str(doc_ids).lower():
                doc_types.add("access logs")
            if "email" in str(doc_ids).lower():
                doc_types.add("email communication")
        
        if not doc_types:
            doc_types = {"various documents", "witness accounts", "physical evidence"}
        
        return ", ".join(sorted(doc_types))
    
    def _create_answer_hint(self, answer: str) -> str:
        """Create a hint about the answer without revealing it."""
        answer_lower = answer.lower()
        
        # Check if it's a person's name
        if " " in answer and len(answer.split()) == 2:
            return "identifying a specific person"
        
        # Check if it's a location
        location_keywords = ["warehouse", "office", "room", "building", "floor"]
        if any(kw in answer_lower for kw in location_keywords):
            return "determining a specific location"
        
        # Check if it's an action/event
        action_keywords = ["leaked", "stole", "accessed", "modified", "deleted"]
        if any(kw in answer_lower for kw in action_keywords):
            return "identifying who performed an action"
        
        # Default
        return "solving a specific question about the events"
    
    def _validate_characters(self, characters: List[Character]):
        """Validate generated characters."""
        if not characters:
            raise ValueError("No characters generated")
        
        if len(characters) < 3:
            raise ValueError(f"Too few characters: {len(characters)} (minimum 3)")
        
        # Check for duplicate names
        names = [c.name for c in characters]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate character names detected")
        
        # Check required fields
        for char in characters:
            if not char.name or not char.role:
                raise ValueError(f"Character missing required fields: {char}")

