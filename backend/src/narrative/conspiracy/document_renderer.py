"""
Document Renderer

Pure rendering layer - generates realistic documents from narrative plans.
No content decisions, just formatting and environmental details.
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
from models.conspiracy import ConspiracyPremise
from .political_context_generator import PoliticalContext
from .document_narrative_planner import DocumentNarrativePlan
from .evidence_fact_extractor import AtomicFact

logger = logging.getLogger(__name__)


class DocumentRenderer:
    """
    Pure renderer - generates realistic documents from narrative plans.
    
    NO CONTENT DECISIONS - only formatting and environmental details.
    """
    
    def __init__(self, llm_client):
        """Initialize renderer with LLM client."""
        self.llm = llm_client
    
    async def render_documents(
        self,
        plans: List[DocumentNarrativePlan],
        characters: List[Dict],
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Render all documents from plans.
        
        Args:
            plans: Complete narrative plans for documents
            characters: Character list
            premise: Conspiracy premise
            political_context: Political context
            config: Optional configuration
        
        Returns:
            List of generated documents
        """
        config = config or {}
        logger.info(f"Rendering {len(plans)} documents from plans")
        
        # Create rendering tasks
        tasks = []
        for plan in plans:
            task = self.render_document(plan, characters, premise, political_context, config)
            tasks.append(task)
        
        # Execute in parallel batches
        batch_size = config.get("parallel_batch_size", 10)
        documents = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            logger.info(f"  Rendering batch {i//batch_size + 1}/{(len(tasks)-1)//batch_size + 1}...")
            
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            # Filter out exceptions and log them
            for idx, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"  ❌ Document in batch failed: {result}")
                else:
                    documents.append(result)
            
            # Delay between batches to avoid rate limits
            if i + batch_size < len(tasks):
                await asyncio.sleep(2.5)
        
        logger.info(f"  ✅ Rendered {len(documents)} documents")
        return documents
    
    async def render_document(
        self,
        plan: DocumentNarrativePlan,
        characters: List[Dict],
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Render a single document from its narrative plan.
        
        The plan contains ALL content decisions:
        - Which facts to include
        - Narrative purpose
        - Document type
        
        The renderer just adds realism.
        """
        config = config or {}
        
        # Format facts for prompt
        facts_list = self._format_facts_for_prompt(plan.required_facts)
        
        # Generate timestamp
        timestamp = self._generate_timestamp()
        
        # Select author
        author = self._select_author(plan.document_type, characters)
        
        # Build simple prompt
        prompt = self._build_prompt(
            plan,
            facts_list,
            author,
            timestamp,
            premise,
            political_context
        )
        
        # Retry logic
        max_retries = config.get("max_retries", 5)
        
        for attempt in range(max_retries):
            try:
                # Generate with LLM
                response = await self.llm.generate_json(
                    prompt,
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 6000)  # Reasonable limit - too high causes issues
                )
                
                # Validate that required facts are present
                self._validate_facts_present(response, plan.required_facts, plan.document_id)
                
                return response
            
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"  ⚠️  Attempt {attempt + 1}/{max_retries} failed for {plan.document_id}: {e}")
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"  ❌ CRITICAL: Failed to render {plan.document_id} after {max_retries} attempts")
                    raise Exception(f"Failed to render document {plan.document_id}: {e}")
    
    def _format_facts_for_prompt(self, facts: List[AtomicFact]) -> str:
        """
        Format atomic facts for prompt.
        
        Normalizes special characters to ASCII to make it easier for LLM.
        """
        if not facts:
            return "No specific facts required."
        
        # Separate answer-critical facts from regular facts
        critical_facts = [f for f in facts if f.is_answer_critical]
        regular_facts = [f for f in facts if not f.is_answer_critical]
        
        lines = []
        
        # Show CRITICAL facts first with emphasis
        if critical_facts:
            lines.append("🔴 CRITICAL ANSWER FACTS (MUST INCLUDE THESE FIRST):")
            lines.append("=" * 60)
            for i, fact in enumerate(critical_facts, 1):
                normalized_value = self._normalize_for_matching(fact.value)
                lines.append(f"{i}. \"{normalized_value}\"")
            lines.append("=" * 60)
            lines.append("")
        
        # Show regular facts
        if regular_facts:
            lines.append("Additional facts to include:")
            for i, fact in enumerate(regular_facts, 1):
                normalized_value = self._normalize_for_matching(fact.value)
                lines.append(f"- \"{normalized_value}\"")
        
        return "\n".join(lines)
    
    def _build_prompt(
        self,
        plan: DocumentNarrativePlan,
        facts_list: str,
        author: str,
        timestamp: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext
    ) -> str:
        """
        Build simple rendering prompt.
        
        No containment warnings - the facts list already contains
        only what should be included.
        """
        prompt = f"""OUTPUT JSON DIRECTLY - NO EXPLANATIONS, NO THINKING, NO COMMENTS.

Generate a realistic {plan.document_type} document.

NARRATIVE PURPOSE:
{plan.narrative_purpose}

SETTING:
{plan.narrative_setting}

TONE: {plan.narrative_tone}
PERSPECTIVE: {plan.perspective}

{facts_list}

CONTEXT:
- World: {political_context.world_name}
- Time Period: {political_context.time_period}
- Conspiracy Type (subtle background): {premise.conspiracy_type}

CRITICAL INSTRUCTIONS:
1. Include ALL required facts listed above (use EXACT values)
2. Keep it BRIEF - MAXIMUM 3-4 entries for logs, 1-2 paragraphs for text
3. Add 1-2 mundane details only
4. COMPLETE the JSON properly - close all strings, objects, and arrays
5. If approaching token limit, END the document cleanly rather than leaving it incomplete

DOCUMENT TYPE GUIDELINES:
{self._get_document_type_guidelines(plan.document_type)}

OUTPUT FORMAT (STRICT JSON):
CRITICAL: Return ONLY valid JSON. NO markdown formatting (**, __, etc.). NO comments.

{{
  "document_id": "{plan.document_id}",
  "document_type": "{plan.document_type}",
  "timestamp": "{timestamp}",
  "author": "{author}",
  "fields": {{
    {self._get_expected_fields(plan.document_type)}
  }}
}}

VALIDATION RULES:
- Use EXACT character values for all required facts (including special characters like ‑, -, etc.)
- Every required fact MUST appear verbatim somewhere in the document
- Double-check that names/IDs match exactly before returning
"""
        return prompt
    
    def _get_document_type_guidelines(self, doc_type: str) -> str:
        """Get concise guidelines for document type."""
        guidelines = {
            "security_access_log": "Structured log entries with timestamps, badge IDs, access times, locations. 3-4 entries max.",
            "internal_email": "from, to, subject, body format. Professional tone, 1-2 short paragraphs.",
            "performance_review": "employee_name, date, reviewer, content. Brief behavioral observations.",
            "encrypted_message": "message_id, sender, recipient, encrypted_content. Technical, secure tone.",
            "meeting_notes": "date, attendees, subject, notes. Brief discussion points and decisions.",
            "system_log": "Structured entries with timestamps, service events. 3-4 entries max.",
            "personnel_file": "employee_name, employee_id, department, notes. Brief activity summary.",
            "incident_report": "report_id, date, reporter, description. Brief incident summary."
        }
        return guidelines.get(doc_type, "Generate appropriate brief format for this document type.")
    
    def _get_expected_fields(self, doc_type: str) -> str:
        """Get expected JSON fields for document type."""
        field_templates = {
            "security_access_log": '"facility": "...", "log_date": "...", "entries": [{"timestamp": "...", "badge_id": "...", "user": "...", "location": "...", "event": "..."}]',
            
            "internal_email": '"from": "...", "to": "...", "subject": "...", "body": "..."',
            
            "performance_review": '"employee_name": "...", "date": "...", "reviewer": "...", "content": "...", "rating": "..."',
            
            "encrypted_message": '"message_id": "...", "sender": "...", "recipient": "...", "encrypted_content": "..."',
            
            "meeting_notes": '"date": "...", "attendees": [...], "subject": "...", "notes": "..."',
            
            "system_log": '"server_name": "...", "log_date": "...", "entries": [{"timestamp": "...", "level": "...", "message": "..."}]',
            
            "financial_record": '"record_id": "...", "date": "...", "amount": "...", "description": "..."',
            
            "personnel_file": '"employee_name": "...", "employee_id": "...", "department": "...", "notes": "..."',
            
            "incident_report": '"report_id": "...", "date": "...", "reporter": "...", "description": "..."',
            
            "research_log": '"log_id": "...", "researcher": "...", "date": "...", "entry": "..."',
        }
        return field_templates.get(doc_type, '"content": "..."')
    
    def _select_author(self, doc_type: str, characters: List[Dict[str, Any]]) -> str:
        """Select appropriate author for document type. Normalizes name to ASCII."""
        # System documents
        if "log" in doc_type or "system" in doc_type:
            return "system"
        
        # Character documents
        if characters:
            char = random.choice(characters)
            name = char.get("name", "Unknown")
            # Normalize to prevent en-dash issues
            return self._normalize_for_matching(name)
        
        return "Author"
    
    def _generate_timestamp(self) -> str:
        """Generate a random recent timestamp."""
        base = datetime.now() - timedelta(days=random.randint(1, 30))
        return base.isoformat()
    
    def _validate_facts_present(
        self,
        document: Dict[str, Any],
        required_facts: List[AtomicFact],
        doc_id: str
    ):
        """
        Validate that all required facts are present in the document.
        
        Normalizes special characters to handle LLM substitutions.
        """
        import json
        import unicodedata
        
        # Normalize document text
        doc_str = json.dumps(document).lower()
        doc_str_normalized = self._normalize_for_matching(doc_str)
        
        missing_facts = []
        for fact in required_facts:
            # Normalize the fact value for matching
            fact_normalized = self._normalize_for_matching(fact.value.lower())
            
            if fact_normalized not in doc_str_normalized:
                missing_facts.append(f"{fact.fact_type}: {fact.value}")
        
        if missing_facts:
            logger.warning(f"  ⚠️  Validation failed for {doc_id}")
            logger.warning(f"      Missing facts: {missing_facts}")
            raise ValueError(f"Required facts missing from document: {missing_facts}")
    
    def _normalize_for_matching(self, text: str) -> str:
        """
        Normalize text for matching - handle special characters and accents that LLMs often substitute.
        
        - Converts en-dash (‑), em-dash (—), minus (−) to regular hyphen (-)
        - Removes accents (á → a, é → e, etc.)
        - Removes zero-width spaces
        - Normalizes Unicode
        """
        import unicodedata
        
        # First normalize Unicode
        text = unicodedata.normalize('NFD', text)
        
        # Remove accents by stripping combining characters
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Recompose
        text = unicodedata.normalize('NFC', text)
        
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
        
        # Normalize all types of spaces to regular space
        text = text.replace('\u00a0', ' ')   # no-break space
        text = text.replace('\u202f', ' ')   # narrow no-break space (PROBLEM CHARACTER!)
        text = text.replace('\u2009', ' ')   # thin space
        text = text.replace('\u2008', ' ')   # punctuation space
        text = text.replace('\u2007', ' ')   # figure space
        text = text.replace('\u2006', ' ')   # six-per-em space
        text = text.replace('\u2005', ' ')   # four-per-em space
        text = text.replace('\u2004', ' ')   # three-per-em space
        text = text.replace('\u2003', ' ')   # em space
        text = text.replace('\u2002', ' ')   # en space
        text = text.replace('\u2000', ' ')   # en quad
        text = text.replace('\u2001', ' ')   # em quad
        
        return text

