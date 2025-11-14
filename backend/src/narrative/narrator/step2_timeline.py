"""Step 2: Timeline Generation for narrative."""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..graph import Character, TimelineEvent


logger = logging.getLogger(__name__)


TIMELINE_GENERATION_PROMPT = """You are creating a timeline of events for a detective mystery.

CHARACTERS (already created):
{characters_summary}

MYSTERY CONTEXT:
- Time range: {time_range_days} days
- Question: {question}
- Answer: {answer}
- Difficulty: {difficulty}/10

PROOF TREE REQUIREMENTS:
{proof_tree_requirements}

YOUR TASK:
Create a chronological timeline of {num_events} key events over {time_range_days} days.

For each event:
- timestamp: Exact date/time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- event_type: Type of event - choose from:
  ["meeting", "transaction", "communication", "access", "incident", "discovery", "routine_activity"]
- description: What happened (2-3 sentences, specific and concrete)
- participants: Which characters were involved (use exact names from character list)
- location: Where it happened
- evidence_created: What documents/traces this event would create
  Example: ["email", "badge_log", "surveillance_log", "receipt"]

IMPORTANT RULES:
- Events must be chronologically ordered
- First event starts around Day 1, 09:00
- Last event around Day {time_range_days}, 17:00
- Spread events realistically across the time period
- Include both suspicious and routine events
- Events should naturally lead to evidence creation
- Make events feel realistic, not contrived
- Some events should be red herrings
- Build tension toward the answer

The timeline should make narrative sense and create opportunities for clues to exist naturally.

Output ONLY valid JSON in this exact format:
{{
  "timeline": [
    {{
      "timestamp": "2024-11-10T09:00:00Z",
      "event_type": "meeting",
      "description": "Specific description of what happened...",
      "participants": ["Character Name 1", "Character Name 2"],
      "location": "Conference Room A",
      "evidence_created": ["email", "calendar_entry"]
    }}
  ]
}}"""


class TimelineGenerator:
    """Generate timeline using LLM."""
    
    def __init__(self, llm_client):
        """
        Initialize timeline generator.
        
        Args:
            llm_client: LLM client (Cerebras or similar)
        """
        self.llm = llm_client
    
    async def generate_timeline(
        self,
        characters: List[Character],
        mystery_context: Dict[str, Any],
        proof_tree: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[TimelineEvent]:
        """
        Generate timeline of events.
        
        Args:
            characters: Characters from Step 1
            mystery_context: Mystery details
            proof_tree: Proof tree structure
            config: Configuration
        
        Returns:
            List of TimelineEvent objects
        """
        logger.info("📅 Step 2: Generating timeline...")
        
        # Determine time range
        time_range = config.get("time_range_days", 7)
        
        # Determine number of events (roughly 2-4 per day)
        num_events = time_range * 3
        
        # Build prompt
        prompt = self._build_prompt(
            characters,
            mystery_context,
            proof_tree,
            time_range,
            num_events
        )
        
        # Generate with LLM
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 2500)
            )
            
            # Parse timeline
            timeline = [
                TimelineEvent.from_dict(event_data)
                for event_data in response.get("timeline", [])
            ]
            
            # Validate and sort
            timeline = self._validate_and_sort_timeline(timeline, characters)
            
            logger.info(f"   ✅ Generated {len(timeline)} events over {time_range} days")
            for i, event in enumerate(timeline[:3]):
                logger.info(f"      {i+1}. {event.timestamp[:10]}: {event.event_type}")
            if len(timeline) > 3:
                logger.info(f"      ... and {len(timeline) - 3} more events")
            
            return timeline
        
        except Exception as e:
            logger.error(f"   ❌ Timeline generation failed: {e}")
            raise
    
    def _build_prompt(
        self,
        characters: List[Character],
        mystery_context: Dict[str, Any],
        proof_tree: Dict[str, Any],
        time_range: int,
        num_events: int
    ) -> str:
        """Build the timeline generation prompt."""
        
        # Summarize characters
        characters_summary = self._summarize_characters(characters)
        
        # Extract proof tree requirements
        proof_requirements = self._extract_proof_requirements(proof_tree)
        
        # Fill prompt template
        prompt = TIMELINE_GENERATION_PROMPT.format(
            characters_summary=characters_summary,
            time_range_days=time_range,
            question=mystery_context.get("question", ""),
            answer=mystery_context.get("answer", ""),
            difficulty=mystery_context.get("difficulty", 5),
            proof_tree_requirements=proof_requirements,
            num_events=num_events
        )
        
        return prompt
    
    def _summarize_characters(self, characters: List[Character]) -> str:
        """Create a summary of characters for the prompt."""
        lines = []
        for char in characters:
            role_access = f"{char.role}"
            if char.access_level:
                role_access += f" (access: {', '.join(char.access_level[:3])})"
            lines.append(f"- {char.name}: {role_access}")
        return "\n".join(lines)
    
    def _extract_proof_requirements(self, proof_tree: Dict[str, Any]) -> str:
        """Extract what events need to happen based on proof tree."""
        nodes = proof_tree.get("inference_nodes", [])
        
        if not nodes:
            return "Events should create opportunities for evidence discovery."
        
        requirements = []
        for node in nodes:
            inference = node.get("inference", "")
            reasoning_type = node.get("reasoning_type", "")
            
            # Create natural event requirements
            if "meeting" in inference.lower():
                requirements.append("- A meeting or communication between key individuals")
            if "access" in inference.lower() or "badge" in str(node).lower():
                requirements.append("- Physical access to a location (creates badge logs)")
            if "transaction" in inference.lower() or "financial" in str(node).lower():
                requirements.append("- A financial transaction or exchange")
            if "timestamp" in inference.lower() or reasoning_type == "temporal_reasoning":
                requirements.append("- Events with precise timing that can be cross-referenced")
        
        if not requirements:
            requirements.append("- Events that naturally create documentary evidence")
        
        return "\n".join(requirements)
    
    def _validate_and_sort_timeline(
        self,
        timeline: List[TimelineEvent],
        characters: List[Character]
    ) -> List[TimelineEvent]:
        """Validate timeline and sort chronologically."""
        
        if not timeline:
            raise ValueError("No timeline events generated")
        
        # Get character names for validation
        character_names = {char.name for char in characters}
        
        # Validate each event
        validated_timeline = []
        for event in timeline:
            # Check participants exist
            valid_participants = [
                p for p in event.participants
                if p in character_names or p.lower() in ["system", "automated", "unknown"]
            ]
            event.participants = valid_participants
            
            # Ensure timestamp is valid
            try:
                datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
                validated_timeline.append(event)
            except ValueError:
                logger.warning(f"   ⚠️  Skipping event with invalid timestamp: {event.timestamp}")
                continue
        
        # Sort chronologically
        validated_timeline.sort(key=lambda e: e.timestamp)
        
        return validated_timeline

