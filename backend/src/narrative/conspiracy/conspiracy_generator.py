"""Conspiracy Premise Generator - creates WHO, WHAT, WHY, HOW answers."""

import logging
import random
from typing import Dict, Any, Tuple
from models.conspiracy import PoliticalContext, ConspiracyPremise, AnswerDimension


logger = logging.getLogger(__name__)


CONSPIRACY_PREMISE_PROMPT = """You are creating a conspiracy mystery premise with 4 answer dimensions.

POLITICAL CONTEXT:
{political_context_summary}

CONSPIRACY TYPE: {conspiracy_type}
DIFFICULTY: {difficulty}/10

YOUR TASK:
Create a multi-layered conspiracy with four distinct but interconnected answers.

THE FOUR DIMENSIONS:

1. WHO - The Conspirators
   - Specific named individuals (2-4 people)
   - Include their roles/affiliations from the political context
   - Make them connected to existing organizations/factions
   - Example: "Agent Marcus Reeves (Directorate) and Dr. Elena Kross (Order of the Veil)"

2. WHAT - The Conspiracy Goal
   - What they're trying to accomplish
   - Should be significant and tie to political context
   - Strongly themed around {conspiracy_type}
   - Make the goal authentically reflect {conspiracy_type} conspiracy beliefs and narratives

3. WHY - The Motivation
   - Why they're doing this
   - Tied to political context (revenge, ideology, survival, power)
   - Personal and/or ideological reasons
   - Examples: "Revenge for a past cover-up that destroyed their mentor"
             "Belief that current reality is an illusion that must be shattered"
             "Desperate to prevent an even greater threat they've discovered"

4. HOW - The Method
   - How they're executing the conspiracy
   - Specific tactics: infiltration, manipulation, ritual, blackmail, etc.
   - Should involve multiple steps/phases
   - Examples: "By blackmailing key officials while secretly gathering ritual components"
             "Through infiltrating both government and corporate systems simultaneously"
             "By manipulating rival factions into conflict while performing hidden rituals"

IMPORTANT:
- WHO names should be specific full names with roles
- WHAT should be concrete and conspiracy-themed
- WHY should be compelling and tied to political context
- HOW should be multi-faceted and clever
- All four should interconnect logically
- Make it feel like a real conspiracy with depth

Output ONLY valid JSON:
{{
  "who": "Full names and roles of conspirators",
  "what": "The conspiracy goal",
  "why": "The motivation",
  "how": "The method/tactics",
  "conspiracy_name": "Operation name or conspiracy title",
  "conspiracy_type": "{conspiracy_type}"
}}"""


class ConspiracyGenerator:
    """Generate conspiracy premise with 4-dimensional answers."""
    
    def __init__(self, llm_client):
        """
        Initialize generator.
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
    
    async def generate_conspiracy(
        self,
        political_context: PoliticalContext,
        difficulty: int = 5,
        conspiracy_type: str = "occult",
        config: Dict[str, Any] = None
    ) -> ConspiracyPremise:
        """
        Generate conspiracy premise with WHO, WHAT, WHY, HOW.
        
        Args:
            political_context: Political backdrop
            difficulty: Complexity level (1-10)
            conspiracy_type: Type of conspiracy
            config: Optional configuration
        
        Returns:
            ConspiracyPremise object
        """
        config = config or {}
        
        logger.info("🕵️  Generating conspiracy premise...")
        logger.info(f"   Type: {conspiracy_type}")
        logger.info(f"   Difficulty: {difficulty}/10")
        
        # Summarize political context for prompt
        context_summary = self._summarize_political_context(political_context)
        
        # Build prompt
        prompt = CONSPIRACY_PREMISE_PROMPT.format(
            political_context_summary=context_summary,
            conspiracy_type=conspiracy_type,
            difficulty=difficulty
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.8),
                max_tokens=config.get("max_tokens", 3000)  # High limit to prevent truncation
            )
            
            # Parse into ConspiracyPremise
            premise = ConspiracyPremise(
                who=response.get("who", "Unknown conspirators"),
                what=response.get("what", "Unknown goal"),
                why=response.get("why", "Unknown motivation"),
                how=response.get("how", "Unknown method"),
                conspiracy_name=response.get("conspiracy_name", "Operation Unknown"),
                conspiracy_type=conspiracy_type,
                difficulty=difficulty
            )
            
            # Log the conspiracy
            logger.info(f"   ✅ Conspiracy generated: {premise.conspiracy_name}")
            logger.info(f"      WHO: {premise.who[:80]}...")
            logger.info(f"      WHAT: {premise.what[:80]}...")
            logger.info(f"      WHY: {premise.why[:80]}...")
            logger.info(f"      HOW: {premise.how[:80]}...")
            logger.info("")
            
            return premise
        
        except Exception as e:
            logger.error(f"   ❌ Conspiracy generation failed: {e}")
            # Return fallback
            return self._create_fallback_conspiracy(
                political_context,
                conspiracy_type,
                difficulty
            )
    
    def _summarize_political_context(self, context: PoliticalContext) -> str:
        """Summarize political context for prompt."""
        lines = []
        
        lines.append(f"World: {context.world_name} ({context.time_period})")
        lines.append("")
        
        if context.shadow_agencies:
            lines.append("Shadow Agencies:")
            for agency in context.shadow_agencies[:3]:
                lines.append(f"  - {agency.get('name')}: {agency.get('role')}")
        
        if context.occult_organizations:
            lines.append("Occult Organizations:")
            for org in context.occult_organizations[:3]:
                lines.append(f"  - {org.get('name')}: {org.get('agenda')}")
        
        if context.competing_factions:
            lines.append("Competing Factions:")
            for faction in context.competing_factions[:3]:
                lines.append(f"  - {faction.get('faction')}: {faction.get('goals')}")
        
        if context.past_events:
            lines.append("Key Past Events:")
            for event in context.past_events[:2]:
                lines.append(f"  - {event.get('event')} ({event.get('date')})")
        
        lines.append("")
        lines.append(f"Public Narrative: {context.public_narrative}")
        lines.append(f"Hidden Reality: {context.hidden_reality}")
        
        return "\n".join(lines)
    
    def _create_fallback_conspiracy(
        self,
        context: PoliticalContext,
        conspiracy_type: str,
        difficulty: int
    ) -> ConspiracyPremise:
        """Create fallback conspiracy if LLM fails."""
        logger.warning("   ⚠️  Using fallback conspiracy")
        
        # Extract names from context
        conspirator_names = []
        if context.occult_organizations:
            org = context.occult_organizations[0]
            conspirator_names.append(f"High Priest of {org.get('name', 'The Order')}")
        if context.shadow_agencies:
            agency = context.shadow_agencies[0]
            conspirator_names.append(f"Director of {agency.get('name', 'The Directorate')}")
        
        who = " and ".join(conspirator_names) if conspirator_names else "Agent Marcus Reeves and Dr. Elena Kross"
        
        fallback_whats = [
            "Perform a ritual to tear the veil between realities",
            "Summon an ancient entity imprisoned centuries ago",
            "Steal forbidden artifacts to gain ultimate power",
            "Infiltrate the government to trigger a reality-altering ceremony"
        ]
        
        fallback_whys = [
            "Revenge for a mentor killed in a past cover-up",
            "Belief that current reality is an illusion that must be broken",
            "Desperate attempt to prevent an even greater cosmic threat",
            "Ideological conviction that humanity must transcend its limitations"
        ]
        
        fallback_hows = [
            "By blackmailing key officials while secretly gathering ritual components",
            "Through infiltrating both government and occult organizations simultaneously",
            "By manipulating rival factions into conflict as a distraction",
            "Using corporate resources to fund covert occult research"
        ]
        
        return ConspiracyPremise(
            who=who,
            what=random.choice(fallback_whats),
            why=random.choice(fallback_whys),
            how=random.choice(fallback_hows),
            conspiracy_name=f"Operation {random.choice(['Nightfall', 'Threshold', 'Eclipse', 'Veil'])}",
            conspiracy_type=conspiracy_type,
            difficulty=difficulty
        )

