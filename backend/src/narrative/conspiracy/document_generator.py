"""Constrained Document Generator - generates documents with strict evidence constraints."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from models.conspiracy import (
    DocumentAssignment,
    EvidenceNode,
    SubGraph,
    ConspiracyPremise,
    PoliticalContext,
    CryptoKey
)
from .phrase_encryptor import PhraseEncryptor


logger = logging.getLogger(__name__)


DOCUMENT_GENERATION_PROMPT = """You are generating a document for a conspiracy mystery.

DOCUMENT TYPE: {doc_type}
AUTHOR/SOURCE: {author}
TIMESTAMP: {timestamp}

CONSPIRACY CONTEXT (for background only - DO NOT reveal directly):
{conspiracy_summary}

POLITICAL CONTEXT:
{political_summary}

YOUR TASK:
Generate a realistic {doc_type} that contains the following evidence fragments:

EVIDENCE TO INCLUDE:
{evidence_list}

CRITICAL CONSTRAINTS:
1. Include ONLY the evidence fragments listed above
2. DO NOT add conclusions or connect the dots
3. Make it feel like a real document from this world
4. Evidence should feel natural, not forced
5. DO NOT reveal the conspiracy directly
6. Use appropriate tone/format for {doc_type}

{doc_type_specific_instructions}

Output ONLY valid JSON:
{{
  "document_id": "{doc_id}",
  "document_type": "{doc_type}",
  "timestamp": "{timestamp}",
  "author": "{author}",
  "fields": {{
    {expected_fields}
  }}
}}"""


DOC_TYPE_INSTRUCTIONS = {
    "email": """
EMAIL FORMAT:
- from: sender email
- to: recipient email(s)
- subject: email subject
- body: email body text
- timestamp: when sent

Keep email tone professional but natural.
""",
    "diary": """
DIARY FORMAT:
- date: diary entry date
- author: who wrote it
- content: diary entry text
- mood: optional mood indicator

Personal, introspective tone. Can show stress, paranoia, thoughts.
""",
    "internal_memo": """
MEMO FORMAT:
- from: sender
- to: recipients
- subject: memo subject
- date: when issued
- content: memo text

Official, bureaucratic tone. Company/agency policy or announcements.
""",
    "badge_log": """
BADGE LOG FORMAT:
- facility: location name
- log_date: date of log
- entries: array of access entries
  - badge_number: badge ID
  - name: person name (if available)
  - entry_time: when scanned
  - location: which door/area
  - notes: optional notes

Technical, automated system output.
""",
    "witness_statement": """
WITNESS STATEMENT FORMAT:
- witness_name: who gave statement
- statement_date: when given
- interviewer: who took statement
- statement: the actual testimony text
- location: where statement was taken

First-person account, conversational but recorded officially.
""",
    "police_report": """
POLICE REPORT FORMAT:
- case_number: unique case ID
- report_date: when filed
- officer_name: reporting officer
- incident_date: when incident occurred
- incident_location: where it happened
- report: description of incident
- evidence_noted: list of evidence items
- status: case status

Official, factual, police/investigative tone.
"""
}


class ConstrainedDocumentGenerator:
    """Generate documents with strict evidence constraints."""
    
    def __init__(self, llm_client):
        """
        Initialize generator.
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
        self.encryptor = PhraseEncryptor()
    
    async def generate_documents(
        self,
        assignments: List[DocumentAssignment],
        subgraphs: List[SubGraph],
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        crypto_keys: List[CryptoKey],
        characters: List[Dict[str, Any]],
        config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate all documents in parallel with constraints.
        
        Args:
            assignments: Document assignments
            subgraphs: Sub-graphs with evidence nodes
            premise: Conspiracy premise
            political_context: Political backdrop
            crypto_keys: Cryptographic keys
            characters: Character list
            config: Optional configuration
        
        Returns:
            List of generated documents
        """
        config = config or {}
        
        logger.info("📝 Generating documents with constraints...")
        logger.info(f"   Documents to generate: {len(assignments)}")
        
        # Create node lookup
        node_lookup = {}
        for sg in subgraphs:
            for node in sg.evidence_nodes:
                node_lookup[node.node_id] = node
        
        # Create crypto key lookup
        key_lookup = {key.key_id: key for key in crypto_keys}
        
        # Create generation tasks
        tasks = []
        for assignment in assignments:
            task = self._generate_single_document(
                assignment,
                node_lookup,
                key_lookup,
                premise,
                political_context,
                characters,
                config
            )
            tasks.append(task)
        
        # Execute in parallel batches
        batch_size = config.get("parallel_batch_size", 10)
        documents = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            logger.info(f"   Generating batch {i//batch_size + 1}/{(len(tasks)-1)//batch_size + 1}...")
            
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            for doc in batch_results:
                if isinstance(doc, Exception):
                    logger.error(f"   ❌ Document generation failed: {doc}")
                else:
                    documents.append(doc)
            
            # Delay between batches to avoid rate limits
            if i + batch_size < len(tasks):
                await asyncio.sleep(2.5)
        
        logger.info(f"   ✅ Generated {len(documents)}/{len(assignments)} documents")
        logger.info("")
        
        return documents
    
    async def _generate_single_document(
        self,
        assignment: DocumentAssignment,
        node_lookup: Dict[str, EvidenceNode],
        key_lookup: Dict[str, CryptoKey],
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        characters: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a single document."""
        
        # Get evidence nodes for this document
        evidence_nodes = [
            node_lookup[node_id]
            for node_id in assignment.evidence_node_ids
            if node_id in node_lookup
        ]
        
        if not evidence_nodes:
            logger.warning(f"   ⚠️  No evidence nodes for {assignment.document_id}")
            return self._create_fallback_document(assignment)
        
        # Build evidence list
        evidence_list = "\n".join([
            f"- {node.content}"
            for node in evidence_nodes
        ])
        
        # Get author (character or system)
        author = self._select_author(assignment.document_type, characters)
        
        # Build prompt
        prompt = self._build_document_prompt(
            assignment,
            evidence_list,
            author,
            premise,
            political_context
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 2000)
            )
            
            # Apply phrase-level encryption if needed
            if assignment.contains_encrypted_phrase:
                response = self._apply_phrase_encryption(
                    response,
                    evidence_nodes,
                    key_lookup
                )
            
            # Validate constraints
            self._validate_constraints(response, assignment, evidence_nodes)
            
            return response
        
        except Exception as e:
            logger.error(f"   ❌ Document generation failed for {assignment.document_id}: {e}")
            return self._create_fallback_document(assignment, evidence_nodes)
    
    def _build_document_prompt(
        self,
        assignment: DocumentAssignment,
        evidence_list: str,
        author: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext
    ) -> str:
        """Build generation prompt for document."""
        
        conspiracy_summary = f"""
Conspiracy Name: {premise.conspiracy_name}
Type: {premise.conspiracy_type}
(Keep this in background - don't reveal directly)
"""
        
        political_summary = f"""
World: {political_context.world_name}
Setting: {political_context.time_period}
"""
        
        # Get doc type specific instructions
        doc_type = assignment.document_type
        specific_instructions = DOC_TYPE_INSTRUCTIONS.get(doc_type, "Generate appropriate fields for this document type.")
        
        # Expected fields based on doc type
        expected_fields = self._get_expected_fields(doc_type)
        
        prompt = DOCUMENT_GENERATION_PROMPT.format(
            doc_type=doc_type,
            author=author,
            timestamp=self._generate_timestamp(),
            conspiracy_summary=conspiracy_summary,
            political_summary=political_summary,
            evidence_list=evidence_list,
            doc_type_specific_instructions=specific_instructions,
            doc_id=assignment.document_id,
            expected_fields=expected_fields
        )
        
        return prompt
    
    def _get_expected_fields(self, doc_type: str) -> str:
        """Get expected JSON fields for document type."""
        field_templates = {
            "email": '"from": "...", "to": "...", "subject": "...", "body": "..."',
            "diary": '"date": "...", "author": "...", "content": "...", "mood": "..."',
            "internal_memo": '"from": "...", "to": "...", "subject": "...", "content": "..."',
            "badge_log": '"facility": "...", "log_date": "...", "entries": [...]',
            "witness_statement": '"witness_name": "...", "statement_date": "...", "statement": "..."',
            "police_report": '"case_number": "...", "officer_name": "...", "report": "..."'
        }
        
        return field_templates.get(doc_type, '"content": "..."')
    
    def _select_author(self, doc_type: str, characters: List[Dict[str, Any]]) -> str:
        """Select appropriate author for document type."""
        import random
        
        # System documents
        if doc_type in ["badge_log", "surveillance_log"]:
            return "system"
        
        # Character documents
        if characters:
            char = random.choice(characters)
            return char.get("name", "Unknown")
        
        return "Author"
    
    def _generate_timestamp(self) -> str:
        """Generate a timestamp for document."""
        import random
        from datetime import datetime, timedelta
        
        # Random time in the last 30 days
        base = datetime.now() - timedelta(days=random.randint(1, 30))
        return base.isoformat()
    
    def _apply_phrase_encryption(
        self,
        document: Dict[str, Any],
        evidence_nodes: List[EvidenceNode],
        key_lookup: Dict[str, CryptoKey]
    ) -> Dict[str, Any]:
        """Apply phrase-level encryption to document."""
        
        # Find crypto nodes
        crypto_nodes = [n for n in evidence_nodes if n.encrypted_phrase]
        
        if not crypto_nodes:
            return document
        
        # Apply encryption to each phrase
        fields = document.get("fields", {})
        
        for node in crypto_nodes:
            if node.encrypted_phrase and node.encryption_type:
                # Find the crypto key
                crypto_key = None
                for key in key_lookup.values():
                    if key.unlocks_node_id == node.node_id:
                        crypto_key = key
                        break
                
                if not crypto_key:
                    logger.warning(f"   ⚠️  No crypto key found for node {node.node_id}")
                    continue
                
                # Encrypt the phrase
                encrypted = self.encryptor.encrypt_phrase(
                    node.encrypted_phrase,
                    node.encryption_type,
                    crypto_key.key_value
                )
                
                # Replace in a text field
                for field_name, field_value in fields.items():
                    if isinstance(field_value, str):
                        # Add encrypted phrase to field
                        fields[field_name] = field_value + f"\n\n[Encrypted]: {encrypted}"
                        if node.key_hint:
                            fields[field_name] += f"\n[{node.key_hint}]"
                        break
        
        document["fields"] = fields
        return document
    
    def _validate_constraints(
        self,
        document: Dict[str, Any],
        assignment: DocumentAssignment,
        evidence_nodes: List[EvidenceNode]
    ):
        """Validate document meets constraints."""
        
        # Check that evidence is present
        import json
        doc_str = json.dumps(document).lower()
        
        for node in evidence_nodes:
            # Check if key terms from evidence appear
            key_terms = [word for word in node.content.lower().split() if len(word) > 4]
            if key_terms:
                present = any(term in doc_str for term in key_terms[:3])
                if not present:
                    logger.warning(f"   ⚠️  Evidence may be missing: {node.content[:50]}...")
    
    def _create_fallback_document(
        self,
        assignment: DocumentAssignment,
        evidence_nodes: List[EvidenceNode] = None
    ) -> Dict[str, Any]:
        """Create a fallback document if generation fails."""
        
        content = "Document content"
        if evidence_nodes:
            content = "\n".join([node.content for node in evidence_nodes])
        
        return {
            "document_id": assignment.document_id,
            "document_type": assignment.document_type,
            "timestamp": self._generate_timestamp(),
            "author": "Unknown",
            "fields": {
                "content": content
            }
        }

