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
Generate a realistic, VERBOSE {doc_type} that contains the following evidence fragments:

EVIDENCE TO INCLUDE:
{evidence_list}

CRITICAL CONSTRAINTS:
1. Include ONLY the evidence fragments listed above
2. DO NOT add conclusions or connect the dots
3. Make it feel like a real document from this world
4. Evidence should feel natural, not forced
5. DO NOT reveal the conspiracy directly
6. Use appropriate tone/format for {doc_type}
7. **VERBOSITY REQUIREMENT**: Generate DETAILED content
   - Technical logs: 8-12 log entries with timestamps, system messages, debug info
   - Emails/memos: 2-4 paragraphs, conversational, detailed context
   - Diaries: personal reflections, detailed thoughts, 2-3 paragraphs
   - The evidence should be HIDDEN in the details, not obvious
8. **STRUCTURED OUTPUT REQUIREMENT**: 
   - For logs: Use ARRAYS of structured objects, NOT text dumps
   - Each log entry should be a separate object with proper fields
   - For emails/diaries: Use proper structured fields (from, to, subject, body)
   - DO NOT use a single "content" field with everything as text
   - Follow the exact JSON schema provided in the format instructions

{doc_type_specific_instructions}

Output ONLY valid JSON with STRUCTURED DATA (arrays of objects, not text dumps):
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
- body: email body text (3-5 paragraphs minimum)
- timestamp: when sent

Professional but natural tone. Include:
- Greeting and context
- Multiple paragraphs with details
- Personal observations or concerns
- References to previous conversations
- Evidence hidden naturally in the narrative
""",
    "diary": """
DIARY FORMAT:
- date: diary entry date
- author: who wrote it
- content: diary entry text (3-5 paragraphs minimum)
- mood: optional mood indicator

Personal, introspective tone. Include:
- Stream of consciousness thoughts
- Detailed descriptions of events and feelings
- Paranoia, stress, internal conflict
- Evidence embedded in personal reflections
- At least 3-4 substantial paragraphs
""",
    "internal_memo": """
MEMO FORMAT:
- from: sender
- to: recipients
- subject: memo subject
- date: when issued
- content: memo text (multiple paragraphs)

Official, bureaucratic tone. Include:
- Formal opening
- Multiple sections or bullet points
- Policy details, procedures, or announcements
- References to departments or protocols
- Evidence hidden in bureaucratic language
""",
    "badge_log": """
BADGE LOG FORMAT:
- facility: location name
- log_date: date of log
- entries: verbose log entries (minimum 10-15 entries)

Generate detailed access log with:
- Timestamps with milliseconds
- Badge scans, door access events
- System messages and status updates
- Occasional warnings or anomalies
- Evidence entries mixed with normal traffic
- Include system boot messages, periodic checks, etc.
Technical, automated system output with lots of detail.
""",
    "witness_statement": """
WITNESS STATEMENT FORMAT:
- witness_name: who gave statement
- statement_date: when given
- interviewer: who took statement
- statement: detailed testimony (3-5 paragraphs minimum)
- location: where statement was taken

First-person account with:
- Detailed description of events
- Personal observations and impressions
- Timeline of what they saw/heard
- Conversational but thorough
- Evidence embedded in their story
""",
    "police_report": """
POLICE REPORT FORMAT:
- case_number: unique case ID
- report_date: when filed
- officer_name: reporting officer
- incident_date: when incident occurred
- incident_location: where it happened
- report: detailed incident description (multiple paragraphs)
- evidence_noted: list of evidence items
- status: case status

Official, factual tone with:
- Thorough chronological description
- Multiple witnesses or observations
- Detailed evidence list
- Officer's professional assessment
- At least 3-4 paragraphs of narrative
""",
    "login_history": """
LOGIN HISTORY FORMAT (STRUCTURED JSON):
- system: authentication system name and version
- log_period_start: start of log period (ISO timestamp)
- log_period_end: end of log period (ISO timestamp)
- authentication_events: ARRAY of 8-12 structured login events

Each authentication_event object must have:
- timestamp: exact login time (ISO format with milliseconds)
- user_id: unique user identifier
- username: human-readable username
- ip_address: source IP
- device: device identifier or name
- event: LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, TIMEOUT, etc.
- status: SUCCESS or FAILED
- notes: optional debug/system messages

Generate 8-12 diverse authentication events with evidence hidden among normal activity.
Include system messages, security warnings, and occasional anomalies.
""",
    "server_log": """
SERVER LOG FORMAT (STRUCTURED JSON):
- server_name: server identifier
- log_date: date of log
- log_level: overall log level (INFO, DEBUG, WARNING)
- entries: ARRAY of 8-12 structured log entries

Each entry object must have:
- timestamp: exact time (ISO format with milliseconds)
- level: INFO, DEBUG, WARNING, ERROR, CRITICAL
- service: service/process name
- message: log message
- details: additional context (optional)

Generate diverse server events: service starts/stops, API calls, health checks, errors.
Evidence should be hidden among normal system activity.
""",
    "firewall_log": """
FIREWALL LOG FORMAT (STRUCTURED JSON):
- firewall_id: firewall device identifier
- log_date: date of log
- entries: ARRAY of 8-12 structured firewall events

Each entry object must have:
- timestamp: exact time (ISO format with milliseconds)
- source_ip: source IP address
- dest_ip: destination IP address
- source_port: source port number
- dest_port: destination port number
- protocol: TCP, UDP, ICMP, HTTPS, etc.
- action: ALLOW, BLOCK, DROP
- rule: firewall rule ID that triggered
- bytes: bytes transferred (optional)

Generate diverse network traffic with evidence connections hidden among normal traffic.
Include allowed and blocked connections, security warnings.
""",
    "network_log": """
NETWORK LOG FORMAT (STRUCTURED JSON):
- network_segment: network segment identifier
- log_date: date of log
- entries: ARRAY of 8-12 structured network events

Each entry object must have:
- timestamp: exact time (ISO format with milliseconds)
- source: source device/IP
- destination: destination device/IP
- protocol: HTTP, HTTPS, SSH, FTP, etc.
- bytes_sent: data sent
- bytes_received: data received
- status: ESTABLISHED, CLOSED, TIMEOUT, etc.
- connection_id: unique connection identifier

Generate diverse network activity with evidence traffic hidden in normal operations.
""",
    "access_control": """
ACCESS CONTROL LOG FORMAT (STRUCTURED JSON):
- facility: facility name
- log_date: date of log
- system_version: access control system version
- entries: ARRAY of 8-12 structured access events
- system_events: ARRAY of 3-5 system status messages

Each access entry object must have:
- timestamp: exact time (ISO format with milliseconds)
- event_type: ACCESS_GRANTED, ACCESS_DENIED, BADGE_SCAN, etc.
- badge_id: badge identifier (hex or alphanumeric)
- user: username or user ID
- clearance_level: numeric clearance level
- zone: security zone
- door: door identifier
- result: GRANTED, DENIED, ERROR
- notes: optional additional information

Generate diverse access events with evidence access hidden among routine badge scans.
Include system messages, security alerts, firmware updates.
""",
    "vpn_log": """
VPN LOG FORMAT (STRUCTURED JSON):
- vpn_gateway: VPN gateway identifier
- log_date: date of log
- entries: ARRAY of 8-12 structured VPN connection events

Each entry object must have:
- timestamp: exact time (ISO format with milliseconds)
- user_id: VPN user identifier
- client_ip: client IP address
- server_ip: VPN server IP
- event: CONNECT, DISCONNECT, AUTH_SUCCESS, AUTH_FAILED
- protocol: OpenVPN, IPSec, WireGuard, etc.
- encryption: encryption method used
- bytes_transferred: data transferred (optional)
- duration: connection duration (optional)

Generate diverse VPN events with evidence connections hidden in routine VPN activity.
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
            
            "diary": '"date": "...", "author": "...", "content": "...", "mood": "...", "entries": [{"time": "...", "text": "..."}]',
            
            "internal_memo": '"from": "...", "to": "...", "subject": "...", "date": "...", "content": "...", "sections": [{"heading": "...", "text": "..."}]',
            
            "badge_log": '"facility": "...", "log_date": "...", "system_version": "...", "entries": [{"timestamp": "...", "badge_id": "...", "user": "...", "location": "...", "event": "...", "status": "..."}]',
            
            "witness_statement": '"witness_name": "...", "statement_date": "...", "interviewer": "...", "location": "...", "statement": "...", "details": [{"question": "...", "answer": "..."}]',
            
            "police_report": '"case_number": "...", "officer_name": "...", "report_date": "...", "incident_date": "...", "incident_location": "...", "report": "...", "evidence_noted": ["..."], "witnesses": [{"name": "...", "statement": "..."}], "status": "..."',
            
            "login_history": '"system": "...", "log_period_start": "...", "log_period_end": "...", "authentication_events": [{"timestamp": "...", "user_id": "...", "username": "...", "ip_address": "...", "device": "...", "event": "...", "status": "...", "notes": "..."}]',
            
            "server_log": '"server_name": "...", "log_date": "...", "log_level": "...", "entries": [{"timestamp": "...", "level": "...", "service": "...", "message": "...", "details": "..."}]',
            
            "firewall_log": '"firewall_id": "...", "log_date": "...", "entries": [{"timestamp": "...", "source_ip": "...", "dest_ip": "...", "source_port": "...", "dest_port": "...", "protocol": "...", "action": "...", "rule": "...", "bytes": "..."}]',
            
            "network_log": '"network_segment": "...", "log_date": "...", "entries": [{"timestamp": "...", "source": "...", "destination": "...", "protocol": "...", "bytes_sent": "...", "bytes_received": "...", "status": "...", "connection_id": "..."}]',
            
            "access_control": '"facility": "...", "log_date": "...", "system_version": "...", "entries": [{"timestamp": "...", "event_type": "...", "badge_id": "...", "user": "...", "clearance_level": "...", "zone": "...", "door": "...", "result": "...", "notes": "..."}], "system_events": [{"timestamp": "...", "event": "..."}]',
            
            "vpn_log": '"vpn_gateway": "...", "log_date": "...", "entries": [{"timestamp": "...", "user_id": "...", "client_ip": "...", "server_ip": "...", "event": "...", "protocol": "...", "encryption": "...", "bytes_transferred": "...", "duration": "..."}]',
            
            "door_access_log": '"facility": "...", "log_date": "...", "entries": [{"timestamp": "...", "door_id": "...", "badge_id": "...", "user": "...", "action": "...", "duration_open": "...", "sensor_status": "..."}]',
            
            "it_inventory": '"department": "...", "inventory_date": "...", "items": [{"asset_id": "...", "device_type": "...", "assigned_to": "...", "location": "...", "serial_number": "...", "status": "...", "notes": "..."}]',
            
            "security_scan": '"scan_id": "...", "scan_date": "...", "scan_type": "...", "results": [{"timestamp": "...", "target": "...", "finding": "...", "severity": "...", "description": "..."}]',
            
            "device_registry": '"registry_date": "...", "devices": [{"device_id": "...", "device_name": "...", "device_type": "...", "mac_address": "...", "ip_address": "...", "owner": "...", "location": "...", "last_seen": "...", "status": "..."}]',
            
            "asset_database": '"database": "...", "query_date": "...", "records": [{"asset_id": "...", "asset_type": "...", "owner": "...", "location": "...", "value": "...", "status": "...", "acquisition_date": "...", "notes": "..."}]',
            
            "phone_record": '"record_date": "...", "calls": [{"timestamp": "...", "caller": "...", "recipient": "...", "duration": "...", "call_type": "...", "notes": "..."}]'
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

