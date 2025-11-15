"""Answer template generator - extracts 4 canonical answers from premise."""

import re
import logging
from typing import Optional
from models.conspiracy import ConspiracyPremise, MysteryAnswer

logger = logging.getLogger(__name__)


class AnswerTemplateGenerator:
    """Extract canonical 4-blank answers from conspiracy premise."""
    
    def extract_from_premise(self, premise: ConspiracyPremise) -> MysteryAnswer:
        """
        Extract simple, atomic answers from premise.
        
        Returns:
            MysteryAnswer with WHO/WHAT/WHERE/WHY filled in
        """
        logger.info("Extracting answer template from premise...")
        
        # WHO: Extract primary conspirator name
        who = self._extract_primary_name(premise.who)
        logger.info(f"   WHO: {who}")
        
        # WHAT: Clean operation name
        what = self._clean_operation_name(premise.conspiracy_name)
        logger.info(f"   WHAT: {what}")
        
        # WHERE: Extract primary location
        where = self._extract_primary_location(premise.how, premise.what)
        logger.info(f"   WHERE: {where}")
        
        # WHY: Core objective
        why = self._extract_core_objective(premise.what)
        logger.info(f"   WHY: {why}")
        
        # Create answer template
        answer = MysteryAnswer(
            who=who,
            what=what,
            where=where,
            why=why
        )
        
        # Generate hash
        answer.combined_hash = answer.generate_hash()
        logger.info(f"   Hash: {answer.combined_hash[:16]}...")
        
        return answer
    
    def _extract_primary_name(self, who_text: str) -> str:
        """
        Extract first full name from 'who' text.
        
        Examples:
            "Dr. Liora Vance and Agent Silas Marlowe" -> "Dr. Liora Vance"
            "Marcus Chen, working with..." -> "Marcus Chen"
        """
        if not who_text:
            return "Unknown"
        
        # Look for patterns like "Dr. Name Surname", "Agent Name", "Name Surname"
        # Match title + two words OR just two words
        patterns = [
            r'\b(Dr\.|Agent|Professor|Senator|Director|Colonel|Captain)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',
            r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, who_text)
            if match:
                if len(match.groups()) == 3:
                    # Title + Name + Surname
                    return f"{match.group(1)} {match.group(2)} {match.group(3)}"
                else:
                    # Name + Surname
                    return f"{match.group(1)} {match.group(2)}"
        
        # Fallback: take first 3-4 words
        words = who_text.split()[:4]
        return ' '.join(words) if words else "Unknown"
    
    def _clean_operation_name(self, name: str) -> str:
        """
        Remove 'Operation' prefix and clean.
        
        Examples:
            "Operation Eclipse Veil" -> "Eclipse Veil"
            "Project Shadow Dawn" -> "Shadow Dawn"
            "Eclipse Veil" -> "Eclipse Veil"
        """
        if not name:
            return "Unknown"
        
        # Remove common prefixes
        for prefix in ["Operation ", "Project ", "Initiative ", "Program "]:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # Limit to 2-3 words max
        words = name.split()[:3]
        return ' '.join(words) if words else "Unknown"
    
    def _extract_primary_location(self, how: str, what: str) -> str:
        """
        Extract key location name from 'how' or 'what' text.
        
        Look for proper nouns that sound like locations.
        """
        text = how + " " + what
        
        # Look for capitalized phrases (likely locations)
        # Pattern: 1-3 capitalized words
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b'
        matches = re.findall(pattern, text)
        
        # Filter out common non-location words
        non_locations = {
            'The', 'A', 'An', 'They', 'Their', 'Operation', 'Project',
            'Agent', 'Dr', 'Professor', 'Director', 'Colonel', 'Captain'
        }
        
        for match in matches:
            # Check if it contains keywords suggesting location
            location_keywords = [
                'Complex', 'Facility', 'Base', 'Site', 'Nexus', 'Chamber',
                'District', 'Sector', 'Zone', 'Harbor', 'Tower', 'Center',
                'Laboratory', 'Institute', 'Vault', 'Mine', 'Mining'
            ]
            
            if any(kw in match for kw in location_keywords):
                return match
            
            # If first word not in non-locations, might be location
            first_word = match.split()[0]
            if first_word not in non_locations and len(match.split()) >= 2:
                return match
        
        # Fallback: try to find compound noun
        words = text.split()
        for i in range(len(words) - 1):
            if words[i][0].isupper() and words[i+1][0].isupper():
                return f"{words[i]} {words[i+1]}"
        
        return "Unknown Location"
    
    def _extract_core_objective(self, what: str) -> str:
        """
        Extract core objective/goal (1-3 words).
        
        Examples:
            "Awaken the ancient deity N'khram" -> "Awaken Void Serpent"
            "Steal classified documents" -> "Steal Documents"
            "Expose government corruption" -> "Expose Corruption"
        """
        if not what:
            return "Unknown"
        
        # Look for verb + noun pattern at start
        # Common action verbs
        action_verbs = [
            'Awaken', 'Steal', 'Expose', 'Destroy', 'Retrieve', 'Obtain',
            'Infiltrate', 'Assassinate', 'Sabotage', 'Reveal', 'Summon',
            'Release', 'Acquire', 'Overthrow', 'Control', 'Manipulate'
        ]
        
        for verb in action_verbs:
            if verb.lower() in what.lower():
                # Find the verb and extract following noun phrase
                pattern = rf'\b{verb}\b.*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
                match = re.search(pattern, what, re.IGNORECASE)
                if match:
                    noun_phrase = match.group(1)
                    return f"{verb} {noun_phrase}"
        
        # Fallback: extract first verb and object
        words = what.split()
        if len(words) >= 2:
            # Try to get verb + noun
            for i, word in enumerate(words[:3]):
                if word[0].isupper() and i > 0:
                    return ' '.join(words[:i+1])
        
        # Last resort: first 2-3 words
        return ' '.join(words[:3]) if len(words) >= 3 else what

