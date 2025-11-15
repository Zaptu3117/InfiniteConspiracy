"""Step 3: Location Generation for narrative."""

import logging
from typing import List, Dict, Any
from narrative.graph import Character, TimelineEvent, Location


logger = logging.getLogger(__name__)


LOCATION_GENERATION_PROMPT = """You are creating locations for a detective mystery setting.

CHARACTERS:
{characters_summary}

TIMELINE EVENTS:
{events_summary}

YOUR TASK:
Create {num_locations} locations (3-8 places) where events in this mystery occur.

For each location:
- name: Location name (specific and memorable)
- type: Location type - choose from:
  ["office", "warehouse", "residence", "public_space", "industrial", "server_room", "meeting_room", "parking_lot"]
- description: 1-2 sentences describing the location
- access_requirements: List of who can access this location
  Use character names OR generic roles like "employees", "public", "security_clearance_required"
- security_level: One of ["public", "restricted", "private", "high_security"]
- surveillance: List of monitoring present
  Example: ["badge_scanners", "security_cameras", "security_guards", "access_logs", "none"]

IMPORTANT:
- Ensure locations match where timeline events occur
- Mix of public and restricted locations
- Varied security levels create investigation opportunities
- Realistic for the setting

Output ONLY valid JSON in this exact format:
{{
  "locations": [
    {{
      "name": "Warehouse 4B",
      "type": "warehouse",
      "description": "Large storage warehouse in the industrial district...",
      "access_requirements": ["employees", "Character Name"],
      "security_level": "restricted",
      "surveillance": ["badge_scanners", "security_cameras"]
    }}
  ]
}}"""


class LocationGenerator:
    """Generate locations using LLM."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def generate_locations(
        self,
        characters: List[Character],
        timeline: List[TimelineEvent],
        config: Dict[str, Any]
    ) -> List[Location]:
        """
        Generate locations for the mystery.
        
        Args:
            characters: Characters from Step 1
            timeline: Timeline from Step 2
            config: Configuration
        
        Returns:
            List of Location objects
        """
        logger.info("🗺️  Step 3: Generating locations...")
        
        # Determine number of locations
        num_locs_range = config.get("num_locations", [3, 8])
        import random
        num_locations = random.randint(num_locs_range[0], num_locs_range[1])
        
        # Build prompt
        prompt = self._build_prompt(
            characters,
            timeline,
            num_locations
        )
        
        # Generate with LLM
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 1500)
            )
            
            # Parse locations
            locations = [
                Location.from_dict(loc_data)
                for loc_data in response.get("locations", [])
            ]
            
            # Validate
            self._validate_locations(locations, timeline)
            
            logger.info(f"   ✅ Generated {len(locations)} locations")
            for loc in locations:
                logger.info(f"      - {loc.name} ({loc.type}, {loc.security_level})")
            
            return locations
        
        except Exception as e:
            logger.error(f"   ❌ Location generation failed: {e}")
            raise
    
    def _build_prompt(
        self,
        characters: List[Character],
        timeline: List[TimelineEvent],
        num_locations: int
    ) -> str:
        """Build the location generation prompt."""
        
        # Summarize characters
        characters_summary = "\n".join([
            f"- {char.name} ({char.role})"
            for char in characters
        ])
        
        # Summarize events with locations mentioned
        events_summary = self._summarize_events(timeline)
        
        # Fill prompt template
        prompt = LOCATION_GENERATION_PROMPT.format(
            characters_summary=characters_summary,
            events_summary=events_summary,
            num_locations=num_locations
        )
        
        return prompt
    
    def _summarize_events(self, timeline: List[TimelineEvent]) -> str:
        """Summarize events focusing on locations."""
        lines = []
        for event in timeline[:10]:  # First 10 events
            lines.append(f"- {event.event_type} at {event.location}")
        if len(timeline) > 10:
            lines.append(f"... and {len(timeline) - 10} more events")
        return "\n".join(lines)
    
    def _validate_locations(self, locations: List[Location], timeline: List[TimelineEvent]):
        """Validate generated locations."""
        if not locations:
            raise ValueError("No locations generated")
        
        if len(locations) < 2:
            raise ValueError(f"Too few locations: {len(locations)} (minimum 2)")
        
        # Check for duplicate names
        names = [loc.name for loc in locations]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate location names detected")
