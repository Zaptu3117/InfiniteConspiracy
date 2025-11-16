"""Political Context Generator - creates fictional political/institutional backdrop."""

import logging
import random
from typing import Dict, Any
from models.conspiracy import PoliticalContext


logger = logging.getLogger(__name__)


POLITICAL_CONTEXT_PROMPT = """You are creating a rich fictional political and institutional backdrop for a conspiracy mystery.

CONSPIRACY TYPE: {conspiracy_type}
DIFFICULTY LEVEL: {difficulty}/10
TONE: Create a narrative world that strongly reflects the {conspiracy_type} conspiracy theme

YOUR TASK:
Create a detailed fictional world with shadow agencies, secret organizations, and hidden power structures that align with the {conspiracy_type} conspiracy theme.

Generate the following elements:

1. SHADOW AGENCIES (2-4): Government branches that operate in secret
   Format: {{"name": "Agency name", "role": "Official role", "agenda": "Hidden agenda"}}

2. SECRET SERVICES (2-3): Intelligence/security organizations
   Format: {{"name": "Service name", "role": "Public function", "agenda": "True purpose"}}

3. OCCULT ORGANIZATIONS (2-4): Secret societies, cults, underground networks
   Format: {{"name": "Organization name", "role": "Cover story", "agenda": "Real goal"}}

4. CORPORATIONS (1-3): Powerful companies involved in conspiracy
   Format: {{"name": "Corp name", "role": "Business", "agenda": "Hidden purpose"}}

5. COMPETING FACTIONS (2-4): Groups fighting for control/influence
   Format: {{"faction": "Name", "rivals": ["Rival names"], "goals": "What they want"}}

6. ALLIANCES (1-3): Secret partnerships between groups
   Format: {{"faction1": "Name", "faction2": "Name", "nature": "Type of alliance"}}

7. PAST EVENTS (2-4): Historical events that shape current tensions
   Format: {{"event": "What happened", "date": "When", "impact": "How it affects now"}}

8. COVER-UPS (1-3): Past conspiracies that were hidden
   Format: {{"incident": "What was covered up", "perpetrators": "Who did it", "evidence": "What remains"}}

9. UNRESOLVED TENSIONS (2-4): Ongoing conflicts/rivalries
   List of tension descriptions

10. RESOURCE CONFLICTS (1-3): What groups are fighting over
    List of resource/power struggles

11. IDEOLOGICAL TENSIONS (1-3): Belief system conflicts
    List of ideological divides

12. PUBLIC NARRATIVE: What the general public believes is happening (1-2 sentences)

13. HIDDEN REALITY: What's actually happening behind the scenes (1-2 sentences)

IMPORTANT:
- Make it feel like a living, complex political landscape
- Create interconnections between organizations
- Some groups should have hidden allegiances
- Past events should influence current motivations
- Make it strongly aligned with the {conspiracy_type} conspiracy theme
- Organizations, events, and motivations should reflect {conspiracy_type} elements

Output ONLY valid JSON in this exact format:
{{
  "world_name": "The Republic" or similar,
  "time_period": "Present Day" or similar,
  "shadow_agencies": [...],
  "secret_services": [...],
  "military_branches": [...],
  "corporations": [...],
  "occult_organizations": [...],
  "competing_factions": [...],
  "alliances": [...],
  "past_events": [...],
  "cover_ups": [...],
  "unresolved_tensions": [...],
  "resource_conflicts": [...],
  "ideological_tensions": [...],
  "public_narrative": "...",
  "hidden_reality": "..."
}}"""


class PoliticalContextGenerator:
    """Generate fictional political context for conspiracy mysteries."""
    
    def __init__(self, llm_client):
        """
        Initialize generator.
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
    
    async def generate_political_context(
        self,
        conspiracy_type: str = "occult",
        difficulty: int = 5,
        config: Dict[str, Any] = None
    ) -> PoliticalContext:
        """
        Generate political/institutional context.
        
        Args:
            conspiracy_type: Type of conspiracy (occult, secret_society, underground_network)
            difficulty: Complexity level (1-10)
            config: Optional configuration
        
        Returns:
            PoliticalContext object
        """
        config = config or {}
        
        logger.info("🌍 Generating political context...")
        logger.info(f"   Type: {conspiracy_type}")
        logger.info(f"   Difficulty: {difficulty}/10")
        
        # Build prompt
        prompt = POLITICAL_CONTEXT_PROMPT.format(
            conspiracy_type=conspiracy_type,
            difficulty=difficulty
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.8),  # Higher for creativity
                max_tokens=config.get("max_tokens", 3000)
            )
            
            # Parse response into PoliticalContext
            context = PoliticalContext(
                world_name=response.get("world_name", "The Republic"),
                time_period=response.get("time_period", "Present Day"),
                shadow_agencies=response.get("shadow_agencies", []),
                secret_services=response.get("secret_services", []),
                military_branches=response.get("military_branches", []),
                corporations=response.get("corporations", []),
                occult_organizations=response.get("occult_organizations", []),
                competing_factions=response.get("competing_factions", []),
                alliances=response.get("alliances", []),
                past_events=response.get("past_events", []),
                cover_ups=response.get("cover_ups", []),
                unresolved_tensions=response.get("unresolved_tensions", []),
                resource_conflicts=response.get("resource_conflicts", []),
                ideological_tensions=response.get("ideological_tensions", []),
                public_narrative=response.get("public_narrative", ""),
                hidden_reality=response.get("hidden_reality", "")
            )
            
            # Log summary
            logger.info(f"   ✅ Political context generated")
            logger.info(f"      World: {context.world_name}")
            logger.info(f"      Shadow agencies: {len(context.shadow_agencies)}")
            logger.info(f"      Occult organizations: {len(context.occult_organizations)}")
            logger.info(f"      Competing factions: {len(context.competing_factions)}")
            logger.info(f"      Past events: {len(context.past_events)}")
            logger.info("")
            
            return context
        
        except Exception as e:
            logger.error(f"   ❌ Political context generation failed: {e}")
            # Return fallback context
            return self._create_fallback_context(conspiracy_type)
    
    def _create_fallback_context(self, conspiracy_type: str) -> PoliticalContext:
        """Create a fallback political context if LLM fails."""
        logger.warning("   ⚠️  Using fallback political context")
        
        return PoliticalContext(
            world_name="The Republic",
            time_period="Present Day",
            shadow_agencies=[
                {"name": "The Directorate", "role": "Oversight", "agenda": "Control information"},
                {"name": "Special Projects Division", "role": "Research", "agenda": "Weaponize occult knowledge"}
            ],
            secret_services=[
                {"name": "Internal Security Bureau", "role": "Counter-intelligence", "agenda": "Monitor occult activity"}
            ],
            occult_organizations=[
                {"name": "The Order of the Veil", "role": "Philosophical society", "agenda": "Summon ancient power"},
                {"name": "The Obsidian Circle", "role": "Study group", "agenda": "Manipulate reality"}
            ],
            corporations=[
                {"name": "Prometheus Industries", "role": "Technology", "agenda": "Profit from hidden knowledge"}
            ],
            competing_factions=[
                {"faction": "The Directorate", "rivals": ["The Order"], "goals": "Maintain status quo"},
                {"faction": "The Order", "rivals": ["Directorate", "Obsidian Circle"], "goals": "Transcend reality"}
            ],
            alliances=[
                {"faction1": "Prometheus Industries", "faction2": "Special Projects", "nature": "Mutual benefit"}
            ],
            past_events=[
                {"event": "The Blackout Incident", "date": "15 years ago", "impact": "Created paranoia about occult threats"},
                {"event": "Director Marlowe's Disappearance", "date": "5 years ago", "impact": "Power vacuum in intelligence"}
            ],
            cover_ups=[
                {"incident": "The Sanctuary Massacre", "perpetrators": "Unknown", "evidence": "Witness reports suppressed"}
            ],
            unresolved_tensions=[
                "Rivalry between traditional intelligence and occult specialists",
                "Corporate exploitation of government research"
            ],
            resource_conflicts=[
                "Access to classified occult artifacts",
                "Control over key research facilities"
            ],
            ideological_tensions=[
                "Rationalism vs mysticism in government policy",
                "Ends justify means vs ethical boundaries"
            ],
            public_narrative="The government maintains order and protects citizens from threats.",
            hidden_reality="Multiple factions compete for control of occult power, with the public kept in the dark."
        )

