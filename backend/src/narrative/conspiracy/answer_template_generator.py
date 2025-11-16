"""Answer template generator - creates discoverable answers from evidence."""

import re
import logging
import json
from typing import Optional
from models.conspiracy import ConspiracyPremise, MysteryAnswer

logger = logging.getLogger(__name__)


class AnswerTemplateGenerator:
    """Create canonical 4-blank answers that are discoverable through investigation."""
    
    def __init__(self, llm_client):
        """
        Initialize with LLM client for semantic extraction.
        
        Args:
            llm_client: LLM client for answer extraction
        """
        self.llm = llm_client
    
    async def extract_from_premise(self, premise: ConspiracyPremise) -> MysteryAnswer:
        """
        Extract DISCOVERABLE answers from premise using LLM semantic understanding.
        
        These answers must be:
        1. Specific and atomic (not sentences)
        2. Findable through investigating documents
        3. Mentioned in identity chains, crypto evidence, or multiple documents
        
        Returns:
            MysteryAnswer with WHO/WHAT/WHY/HOW filled in
        """
        logger.info("Creating discoverable answer template from premise using LLM...")
        
        # Build extraction prompt
        prompt = f"""You are extracting discoverable answers from a conspiracy premise for a detective mystery game.

CONSPIRACY PREMISE:
WHO: {premise.who}
WHAT: {premise.what}
WHY: {premise.why}
HOW: {premise.how}
CONSPIRACY NAME: {premise.conspiracy_name}

TASK: Extract 4 short, discoverable answers that players can find through investigation.

RULES FOR EXTRACTION:

1. WHO (Primary Conspirator Name):
   - Extract the FULL NAME of the PRIMARY conspirator (first person mentioned)
   - Include title if present (Dr., Colonel, Professor, etc.)
   - Must be 2-4 words (e.g., "Dr. Althea Voss" or "Colonel Marcus Kline")
   - This exact name will appear in identity documents (badge logs, login records, etc.)

2. WHAT (Operation Codename):
   - Extract the operation/project name from CONSPIRACY NAME
   - Remove prefixes like "Operation", "Project", "Initiative"
   - Keep it 2-3 words maximum (e.g., "Abyssal Convergence", "Eclipse Veil")
   - This will appear in encrypted documents and secret communications

3. WHY (Key Phrase - Concrete & Discoverable):
   - Extract a CONCRETE phrase that will appear verbatim in documents
   - Can be: motto ("The Veil Must Fall"), concept phrase ("Break the Accord"), ritual/artifact name ("Obsidian Codex")
   - Must be 2-5 words, memorable, specific, NOT abstract
   - This exact phrase will appear in character dialogue, diaries, or memos
   - Examples: "The Veil Must Fall", "Break the Midnight Accord", "Obsidian Codex Ritual"

4. HOW (Method Phrase - SHORT & Memorable):
   - Extract a SHORT, memorable method/tactic (MAX 5 WORDS!)
   - Should be 2-5 words, concise but specific
   - Can be: action phrase ("Infiltrate Black Vault"), tactic ("Phase One Protocol"), or technical term ("Sigil-Encoded Merger")
   - This MUST be a METHOD/ACTION, NOT a person's name
   - This exact phrase will appear in planning docs or technical memos
   - CRITICAL: Keep it SHORT so LLM can embed it in documents without hitting token limits
   - CRITICAL: Include full details, not just first few words!

OUTPUT FORMAT (JSON only, no explanation):
{{
  "who": "Full primary conspirator name",
  "what": "Operation codename without prefix",
  "why": "Verb phrase motivation",
  "how": "Verb phrase method"
}}

CRITICAL: Ensure HOW is an ACTION/METHOD, not a person name. If the HOW text is complex, focus on the first actionable step.

Generate the JSON now:"""

        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=0.3,  # Low temperature for consistent extraction
                max_tokens=1000  # High limit to prevent truncation
            )
            
            # Validate response
            if not response or not isinstance(response, dict):
                logger.error("LLM returned invalid response, falling back to simple extraction")
                return self._fallback_extraction(premise)
            
            # Extract values with validation
            who = response.get("who", "").strip()
            what = response.get("what", "").strip()
            why = response.get("why", "").strip()
            how = response.get("how", "").strip()
            
            # Validate extracted values
            if not who or len(who.split()) < 2:
                logger.warning(f"WHO too short: '{who}', using fallback")
                who = self._fallback_extract_who(premise.who)
            
            if not what or len(what.split()) > 4:
                logger.warning(f"WHAT invalid: '{what}', using fallback")
                what = self._fallback_extract_what(premise.conspiracy_name)
            
            if not why or len(why.split()) < 2:
                logger.warning(f"WHY too short: '{why}', using fallback")
                why = self._fallback_extract_why(premise.why)
            
            if not how or len(how.split()) < 2:
                logger.warning(f"HOW too short: '{how}', using fallback")
                how = self._fallback_extract_how(premise.how)
            
            # Additional validation: HOW should not be a person name
            if self._looks_like_person_name(how):
                logger.warning(f"HOW looks like person name: '{how}', re-extracting")
                how = self._fallback_extract_how(premise.how)
            
            # NORMALIZE to ASCII (replace en-dashes, em-dashes with regular hyphens)
            who = self._normalize_to_ascii(who)
            what = self._normalize_to_ascii(what)
            why = self._normalize_to_ascii(why)
            how = self._normalize_to_ascii(how)
            
            logger.info(f"   WHO: {who}")
            logger.info(f"   WHAT: {what}")
            logger.info(f"   WHY: {why}")
            logger.info(f"   HOW: {how}")
            
            # Create answer template
            answer = MysteryAnswer(
                who=who,
                what=what,
                why=why,
                how=how
            )
            
            # Generate hash
            answer.combined_hash = answer.generate_hash()
            logger.info(f"   Hash: {answer.combined_hash[:16]}...")
            logger.info("")
            logger.info("   ⚠️  IMPORTANT: These answers MUST appear in documents!")
            logger.info(f"      - {who} must be in identity chains (badge logs, network logs, etc.)")
            logger.info(f"      - {what} must be in encrypted documents or references")
            logger.info(f"      - {why} must be inferable from psychological evidence")
            logger.info(f"      - {how} must be in method descriptions or evidence")
            logger.info("")
            
            return answer
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}, using fallback")
            return self._fallback_extraction(premise)
    
    def _fallback_extraction(self, premise: ConspiracyPremise) -> MysteryAnswer:
        """Fallback to simple extraction if LLM fails."""
        logger.warning("Using fallback extraction (simple rules)")
        
        who = self._fallback_extract_who(premise.who)
        what = self._fallback_extract_what(premise.conspiracy_name)
        why = self._fallback_extract_why(premise.why)
        how = self._fallback_extract_how(premise.how)
        
        answer = MysteryAnswer(who=who, what=what, why=why, how=how)
        answer.combined_hash = answer.generate_hash()
        
        return answer
    
    def _looks_like_person_name(self, text: str) -> bool:
        """Check if text looks like a person name (title + firstname + lastname)."""
        words = text.strip().split()
        if len(words) < 2:
            return False
        
        # Check for title + capitalized words pattern
        titles = ["Dr.", "Dr", "Professor", "Colonel", "Agent", "Director", "Senator", "Captain"]
        has_title = any(text.startswith(t) for t in titles)
        
        # Check if all words are capitalized (typical for names)
        all_capitalized = all(w[0].isupper() for w in words if w)
        
        # If it has a title AND capitalized words, likely a person
        # OR if it's 2-3 capitalized words without action verbs
        action_verbs = ["infiltrate", "sabotage", "blackmail", "deploy", "control", "manipulate", 
                       "hack", "steal", "destroy", "activate", "trigger"]
        has_action = any(verb in text.lower() for verb in action_verbs)
        
        return (has_title and all_capitalized) or (all_capitalized and not has_action and len(words) <= 3)
    
    def _normalize_to_ascii(self, text: str) -> str:
        """
        Normalize text to ASCII - replace en-dashes, em-dashes with regular hyphens.
        """
        import unicodedata
        
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Replace ALL types of dashes/hyphens with regular hyphen
        text = text.replace('\u2010', '-')  # hyphen
        text = text.replace('\u2011', '-')  # non-breaking hyphen
        text = text.replace('\u2012', '-')  # figure dash
        text = text.replace('\u2013', '-')  # en dash
        text = text.replace('\u2014', '-')  # em dash
        text = text.replace('\u2015', '-')  # horizontal bar
        text = text.replace('\u2212', '-')  # minus sign
        text = text.replace('\u00ad', '')    # soft hyphen
        text = text.replace('\u200b', '')    # zero-width space
        text = text.replace('\u2043', '-')  # hyphen bullet
        text = text.replace('\ufe63', '-')  # small hyphen-minus
        text = text.replace('\uff0d', '-')  # fullwidth hyphen-minus
        
        return text
    
    def _fallback_extract_who(self, who_text: str) -> str:
        """Fallback extraction for WHO using simple rules."""
        if not who_text:
            return "Unknown Conspirator"
        
        # Look for patterns: Title + FirstName + LastName OR FirstName + LastName
        # Match the FIRST occurrence (the primary conspirator)
        patterns = [
            # Title + First + Last (e.g., "Dr. Althea Voss")
            r'\b(Dr\.|Agent|Professor|Senator|Director|Colonel|Captain)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',
            # First + Last (e.g., "Marcus Kline")
            r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, who_text)
            if match:
                if len(match.groups()) == 3:
                    # Has title
                    return f"{match.group(1)} {match.group(2)} {match.group(3)}"
                else:
                    # No title
                    return f"{match.group(1)} {match.group(2)}"
        
        # Fallback: take first 3 words max
        words = who_text.split()[:3]
        name = ' '.join(words) if words else "Unknown"
        
        # Clean up parentheses
        name = re.sub(r'\([^)]*\)', '', name).strip()
        return name if name else "Unknown Conspirator"
    
    def _fallback_extract_what(self, conspiracy_name: str) -> str:
        """Fallback extraction for WHAT using simple rules."""
        if not conspiracy_name:
            return "Unknown Operation"
        
        # Remove common prefixes
        for prefix in ["Operation ", "Project ", "Initiative ", "Program ", "Plan "]:
            if conspiracy_name.startswith(prefix):
                conspiracy_name = conspiracy_name[len(prefix):]
        
        # Take first 2-3 words (operation codenames are short)
        words = conspiracy_name.split()[:3]
        codename = ' '.join(words) if words else "Unknown"
        
        return codename
    
    def _fallback_extract_why(self, why_text: str) -> str:
        """Fallback extraction for WHY using simple rules."""
        # Simple extraction: look for key goal words
        goal_words = ["immortality", "power", "control", "dominance", "supremacy", "knowledge", 
                     "reality", "world", "entity", "portal", "gateway"]
        
        for goal in goal_words:
            if goal in why_text.lower():
                return f"Achieve {goal.capitalize()}"
        
        # Extract first capitalized phrase
        words = why_text.split()[:10]
        cap_words = [w for w in words if w and w[0].isupper() and len(w) > 3]
        if len(cap_words) >= 2:
            return f"Control {cap_words[0]} {cap_words[1]}"
        
        return "Achieve Power"
    
    def _fallback_extract_how(self, how_text: str) -> str:
        """Fallback extraction for HOW using simple rules."""
        if not how_text:
            return "Unknown Method"
        
        # Look for Phase 1 or first mentioned action
        phase1_match = re.search(r'Phase\s*1:?\s*([^.;]+)', how_text, re.IGNORECASE)
        if phase1_match:
            phase1_text = phase1_match.group(1)
        else:
            # Use beginning of text
            phase1_text = how_text[:200]  # First 200 chars
        
        # Look for action verbs + targets
        method_patterns = [
            r'\b(infiltrate|sabotage|blackmail|manipulate|deploy|hijack)\b.*?\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
            r'\b(use|leverage|exploit)\b.*?\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, phase1_text, re.IGNORECASE)
            if match:
                verb = match.group(1).capitalize()
                target = match.group(2)
                return f"{verb} {target}"
        
        # Fallback: look for any capitalized org/entity in how
        entity_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b', how_text)
        if entity_matches:
            # Find first action verb
            action_verbs = ['Infiltrate', 'Sabotage', 'Use', 'Deploy', 'Manipulate', 'Control', 'Exploit']
            for verb in action_verbs:
                if verb.lower() in how_text.lower():
                    return f"{verb} {entity_matches[0]}"
            return f"Infiltrate {entity_matches[0]}"
        
        # Last resort: extract key words
        words = phase1_text.split()[:4]
        return ' '.join(words) if words else "Unknown Method"

