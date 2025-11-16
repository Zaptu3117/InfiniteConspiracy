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
            
            batch_results = await asyncio.gather(*batch)
            documents.extend(batch_results)
            
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
                    max_tokens=config.get("max_tokens", 3000)
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
        
        Simple and direct - no containment logic.
        """
        if not facts:
            return "No specific facts required."
        
        lines = ["REQUIRED FACTS TO INCLUDE:"]
        lines.append("=" * 60)
        
        for i, fact in enumerate(facts, 1):
            lines.append(f"\n{i}. {fact.fact_type}: {fact.value}")
        
        lines.append("\n" + "=" * 60)
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
        prompt = f"""Generate a realistic {plan.document_type} document.

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

INSTRUCTIONS:
1. Include ALL required facts listed above (use exact values)
2. Add realistic environmental details:
   - For logs: timestamps, system messages, other mundane entries
   - For emails/memos: natural conversation flow, greetings, context
   - For reports: proper formatting, official tone
3. Make it feel like a real document from this world
4. Weave facts naturally into the content
5. Generate DETAILED content:
   - Technical logs: 8-12 entries
   - Emails/documents: 2-4 paragraphs minimum
   - Hide evidence in details, not obvious

DOCUMENT TYPE GUIDELINES:
{self._get_document_type_guidelines(plan.document_type)}

OUTPUT FORMAT (JSON):
{{
  "document_id": "{plan.document_id}",
  "document_type": "{plan.document_type}",
  "timestamp": "{timestamp}",
  "author": "{author}",
  "fields": {{
    {self._get_expected_fields(plan.document_type)}
  }}
}}
"""
        return prompt
    
    def _get_document_type_guidelines(self, doc_type: str) -> str:
        """Get specific guidelines for document type."""
        guidelines = {
            "security_access_log": """
- Format: Structured log entries with timestamps
- Include: Badge IDs, access times, locations, door IDs
- Add mundane entries mixed with evidence
- System boot messages, periodic checks
""",
            "internal_email": """
- Format: from, to, subject, body
- Include: Natural conversation, greetings
- Add: References to meetings, previous emails
- Tone: Professional but natural
""",
            "performance_review": """
- Format: employee_name, date, reviewer, content, rating
- Include: Behavioral observations, work quality
- Add: Specific examples, timeline
- Tone: Professional, evaluative
""",
            "encrypted_message": """
- Format: message_id, sender, recipient, encrypted_content
- Include: Encrypted phrases, cipher hints
- Add: Message metadata, routing info
- Tone: Technical, secure
""",
            "meeting_notes": """
- Format: date, attendees, subject, notes
- Include: Discussion points, decisions
- Add: Action items, follow-ups
- Tone: Informal but organized
""",
            "system_log": """
- Format: Structured entries with timestamps
- Include: Service events, API calls, errors
- Add: System status, health checks
- Tone: Technical, automated
"""
        }
        return guidelines.get(doc_type, "Generate appropriate format for this document type.")
    
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
        """Select appropriate author for document type."""
        # System documents
        if "log" in doc_type or "system" in doc_type:
            return "system"
        
        # Character documents
        if characters:
            char = random.choice(characters)
            return char.get("name", "Unknown")
        
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
        
        Simple validation - just check if fact values appear in document.
        """
        import json
        doc_str = json.dumps(document).lower()
        
        missing_facts = []
        for fact in required_facts:
            if fact.value.lower() not in doc_str:
                missing_facts.append(f"{fact.fact_type}: {fact.value}")
        
        if missing_facts:
            logger.warning(f"  ⚠️  Validation failed for {doc_id}")
            logger.warning(f"      Missing facts: {missing_facts}")
            raise ValueError(f"Required facts missing from document: {missing_facts}")

