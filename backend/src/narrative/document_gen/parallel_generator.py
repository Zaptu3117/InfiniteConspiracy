"""Parallel document generation using narrative graph."""

import asyncio
import logging
from typing import List, Dict, Any
import json

from narrative.graph import NarrativeGraph, DocumentPlan, Character
from .document_prompts import get_document_prompt_template


logger = logging.getLogger(__name__)


class ParallelDocumentGenerator:
    """Generate all documents in parallel using narrative graph context."""
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        """
        Initialize parallel generator.
        
        Args:
            llm_client: LLM client for generation
            config: Configuration dictionary
        """
        self.llm = llm_client
        self.config = config
    
    async def generate_all_documents(
        self,
        narrative_graph: NarrativeGraph
    ) -> List[Dict[str, Any]]:
        """
        Generate all documents in parallel using the complete narrative graph.
        
        Args:
            narrative_graph: Complete narrative graph from narrator
        
        Returns:
            List of generated document dictionaries
        """
        logger.info("="*60)
        logger.info("📄 STARTING PARALLEL DOCUMENT GENERATION")
        logger.info("="*60)
        logger.info(f"Generating {len(narrative_graph.document_plan)} documents...")
        logger.info("")
        
        # Create generation tasks
        tasks = []
        for doc_plan in narrative_graph.document_plan:
            task = self._generate_single_document(
                doc_plan,
                narrative_graph
            )
            tasks.append(task)
        
        # Execute in parallel with limit
        parallel_limit = self.config.get("parallel_limit", 10)
        
        if len(tasks) <= parallel_limit:
            # Generate all at once
            documents = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Generate in batches
            documents = []
            for i in range(0, len(tasks), parallel_limit):
                batch = tasks[i:i+parallel_limit]
                logger.info(f"   Generating batch {i//parallel_limit + 1}/{(len(tasks)-1)//parallel_limit + 1}...")
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                documents.extend(batch_results)
        
        # Filter out exceptions
        successful_docs = []
        failed_count = 0
        
        for i, doc in enumerate(documents):
            if isinstance(doc, Exception):
                logger.error(f"   ❌ Document {i+1} failed: {doc}")
                failed_count += 1
            else:
                successful_docs.append(doc)
        
        logger.info("")
        logger.info("="*60)
        logger.info("✅ DOCUMENT GENERATION COMPLETE")
        logger.info("="*60)
        logger.info(f"Success: {len(successful_docs)}/{len(documents)} documents")
        if failed_count > 0:
            logger.warning(f"Failed: {failed_count} documents")
        logger.info("")
        
        return successful_docs
    
    async def _generate_single_document(
        self,
        doc_plan: DocumentPlan,
        graph: NarrativeGraph
    ) -> Dict[str, Any]:
        """
        Generate a single document using full narrative graph context.
        
        Args:
            doc_plan: Document plan specification
            graph: Complete narrative graph
        
        Returns:
            Generated document dictionary
        """
        try:
            # Get author character
            author = graph.get_character(doc_plan.author)
            
            # Get referenced documents
            referenced_docs = graph.get_referenced_documents(doc_plan.doc_id)
            
            # Get timeline context
            timeline_context = graph.get_timeline_context(doc_plan.timestamp)
            
            # Build prompt
            prompt = self._build_document_prompt(
                doc_plan,
                author,
                referenced_docs,
                timeline_context,
                graph
            )
            
            # Generate content
            content = await self.llm.generate_json(
                prompt,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2000)
            )
            
            # Add metadata
            content["document_id"] = doc_plan.doc_id
            content["document_type"] = doc_plan.doc_type
            
            # Validate clues present
            self._validate_clues_present(content, doc_plan)
            
            # CRITICAL: Validate information containment
            self._validate_information_containment(content, doc_plan)
            
            return content
        
        except Exception as e:
            logger.error(f"   ❌ Failed to generate {doc_plan.doc_id}: {e}")
            raise
    
    def _build_document_prompt(
        self,
        doc_plan: DocumentPlan,
        author: Character,
        referenced_docs: List[DocumentPlan],
        timeline_context: List,
        graph: NarrativeGraph
    ) -> str:
        """Build the prompt for a specific document."""
        
        # Get base template
        template = get_document_prompt_template(doc_plan.doc_type)
        
        # Build context strings
        story_context = self._build_story_context(graph, doc_plan)
        timeline_context_str = self._build_timeline_context(timeline_context)
        referenced_docs_str = self._build_referenced_docs(referenced_docs)
        clues_list_str = self._build_clues_list(doc_plan.clues_to_include)
        
        # Fill template with specific values
        prompt_vars = {
            # Author info
            "author_name": author.name if author else doc_plan.author,
            "author_role": author.role if author else "Unknown",
            "author_background": author.background if author else "",
            "author_personality": author.personality if author else "",
            "author_email": self._generate_email(author.name if author else doc_plan.author),
            
            # Timing
            "timestamp": doc_plan.timestamp,
            "date": doc_plan.timestamp[:10],
            "time": doc_plan.timestamp[11:19],
            
            # Context
            "story_context": story_context,
            "timeline_context": timeline_context_str,
            "referenced_docs": referenced_docs_str,
            "clues_list": clues_list_str,
            
            # Type-specific
            "tone": self._determine_tone(doc_plan, author),
            "recipients": self._get_recipients(doc_plan, graph),
            "recipients_json": json.dumps(self._get_recipients(doc_plan, graph)),
            
            # Document-specific fields
            "facility_name": self._get_location_name(doc_plan, graph),
            "log_period": doc_plan.timestamp[:10],
            "officer_name": doc_plan.author,
            "incident_date": doc_plan.timestamp[:10],
            "incident_details": self._get_incident_details(doc_plan, timeline_context),
            "witness_name": doc_plan.author,
            "witness_background": author.background if author else "",
            "witnessed_events": self._get_witnessed_events(timeline_context),
            "account_holder": doc_plan.author,
            "account_number": self._generate_account_number(),
            "period": doc_plan.timestamp[:7],
            "reporter_name": doc_plan.author,
            "publication_name": "City Times",
            "article_topic": doc_plan.purpose,
            "from_person": doc_plan.author,
            "from_role": author.role if author else "",
            "to_person": self._get_recipients(doc_plan, graph)[0] if self._get_recipients(doc_plan, graph) else "All Staff",
            "subject": doc_plan.purpose[:50],
            "phone_number": self._generate_phone_number(),
            "merchant_name": "Local Store",
            "location": self._get_location_name(doc_plan, graph),
            "operator": "Security",
            "patient_name": doc_plan.author,
            "doctor_name": self._get_doctor_name(graph),
            "visit_type": "Routine checkup"
        }
        
        # Fill template
        try:
            prompt = template.format(**prompt_vars)
        except KeyError as e:
            logger.warning(f"   ⚠️  Missing template variable: {e}")
            # Fill with defaults
            for key in ["tone", "recipients", "facility_name"]:
                if key not in prompt_vars:
                    prompt_vars[key] = ""
            prompt = template.format(**{k: v for k, v in prompt_vars.items()})
        
        return prompt
    
    def _build_story_context(self, graph: NarrativeGraph, doc_plan: DocumentPlan) -> str:
        """Build story context summary (WITHOUT revealing the mystery!)."""
        context_parts = []
        context_parts.append(f"Setting: Corporate/industrial environment")
        # DO NOT include mystery question - documents should only contain raw evidence!
        # context_parts.append(f"Mystery: {graph.mystery_question}")
        context_parts.append(f"Document purpose: {doc_plan.purpose}")
        return "\n".join(context_parts)
    
    def _build_timeline_context(self, timeline_context: List) -> str:
        """Build timeline context string."""
        if not timeline_context:
            return "No prior events"
        
        lines = []
        for event in timeline_context[-5:]:  # Last 5 events
            lines.append(f"- {event.timestamp[:16]}: {event.description}")
        return "\n".join(lines)
    
    def _build_referenced_docs(self, referenced_docs: List[DocumentPlan]) -> str:
        """Build referenced documents string."""
        if not referenced_docs:
            return "No other documents to reference"
        
        lines = []
        for doc in referenced_docs:
            lines.append(f"- {doc.doc_id} ({doc.doc_type}) by {doc.author}")
        return "\n".join(lines)
    
    def _build_clues_list(self, clues: List) -> str:
        """Build clues list string with strict evidence-only warning."""
        if not clues:
            return "No specific elements required"
        
        lines = [
            "⚠️ CRITICAL: ONLY include RAW EVIDENCE below - NO conclusions, NO answers!",
            "Example RAW EVIDENCE: 'User ID xyz123 at 10:03 PM' (NOT 'John Smith deleted files')",
            ""
        ]
        for clue in clues:
            lines.append(f"- Include: {clue.clue_data} (in field: {clue.field_to_insert})")
        return "\n".join(lines)
    
    def _determine_tone(self, doc_plan: DocumentPlan, author: Character) -> str:
        """Determine appropriate tone."""
        if doc_plan.is_red_herring:
            return "casual"
        if author and "anxious" in author.personality.lower():
            return "concerned"
        return "professional"
    
    def _get_recipients(self, doc_plan: DocumentPlan, graph: NarrativeGraph) -> List[str]:
        """Get email recipients."""
        # Use characters who might be involved
        if graph.characters:
            return [graph.characters[0].name]
        return ["Recipient"]
    
    def _get_location_name(self, doc_plan: DocumentPlan, graph: NarrativeGraph) -> str:
        """Get location name."""
        if graph.locations:
            return graph.locations[0].name
        return "Office Building"
    
    def _get_incident_details(self, doc_plan: DocumentPlan, timeline_context: List) -> str:
        """Get incident details."""
        if timeline_context:
            return timeline_context[-1].description
        return doc_plan.purpose
    
    def _get_witnessed_events(self, timeline_context: List) -> str:
        """Get witnessed events."""
        if timeline_context:
            return timeline_context[-1].description
        return "Observed events"
    
    def _get_doctor_name(self, graph: NarrativeGraph) -> str:
        """Get doctor name."""
        for char in graph.characters:
            if "doctor" in char.role.lower() or "medical" in char.role.lower():
                return char.name
        return "Dr. Smith"
    
    def _generate_email(self, name: str) -> str:
        """Generate email address."""
        name_part = name.lower().replace(" ", ".")
        return f"{name_part}@company.com"
    
    def _generate_account_number(self) -> str:
        """Generate account number."""
        import random
        return f"{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    
    def _generate_phone_number(self) -> str:
        """Generate phone number."""
        import random
        return f"555-{random.randint(100,999)}-{random.randint(1000,9999)}"
    
    def _validate_clues_present(self, content: Dict[str, Any], doc_plan: DocumentPlan):
        """Validate that required clues are present in generated content."""
        content_str = json.dumps(content).lower()
        
        for clue in doc_plan.clues_to_include:
            clue_data_lower = clue.clue_data.lower()
            
            # Extract key terms from the clue (words longer than 4 characters)
            key_terms = [word for word in clue_data_lower.split() if len(word) > 4 and word.isalnum()]
            
            # Check if at least 50% of key terms are present (more lenient)
            if key_terms:
                present_count = sum(1 for term in key_terms if term in content_str)
                if present_count / len(key_terms) < 0.5:
                    logger.warning(
                        f"   ⚠️  Clue '{clue.clue_data}' may be missing or paraphrased in {doc_plan.doc_id}"
                    )
            elif clue_data_lower not in content_str:
                # Fallback to exact match for short clues
                logger.warning(
                    f"   ⚠️  Clue '{clue.clue_data}' not found in {doc_plan.doc_id}"
                )
    
    def _validate_information_containment(self, content: Dict[str, Any], doc_plan: DocumentPlan):
        """
        CRITICAL: Check if document is leaking TOO MUCH information.
        Each document should contain ONLY small fragments, not connected chains.
        """
        content_str = json.dumps(content).lower()
        
        # Extract all technical identifiers that might be in the document
        import re
        
        # Find user IDs (patterns like: userid, user_id, jsmith, mpatel, lramirez)
        user_ids = re.findall(r'\b[a-z]+\d*[a-z]*\b(?=\s+(?:logged|accessed|initiated|executed|deleted))', content_str)
        
        # Find IPs
        ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', content_str)
        
        # Find badge numbers
        badges = re.findall(r'(?:badge|badge_number|badge_id)\s*[#:]?\s*["\']?(\d+|[A-Z]?\d+)', content_str)
        
        # Find session IDs, request IDs, transaction IDs
        session_ids = re.findall(r'(?:session|request|transaction|ticket)\s*[#:]?\s*["\']?([A-Z0-9\-]+)', content_str)
        
        # Check for dangerous combinations in the SAME document
        warnings = []
        
        # DANGER: User ID + IP in same doc (direct connection!)
        if len(user_ids) > 0 and len(ips) > 0:
            warnings.append(f"⚠️  Contains BOTH user ID ({user_ids[0]}) AND IP ({ips[0]}) - TOO CONNECTED!")
        
        # DANGER: User ID + Badge in same doc
        if len(user_ids) > 0 and len(badges) > 0:
            warnings.append(f"⚠️  Contains BOTH user ID ({user_ids[0]}) AND badge ({badges[0]}) - TOO CONNECTED!")
        
        # DANGER: Multiple linking identifiers (session + user + IP)
        if len(session_ids) > 0 and len(user_ids) > 0 and len(ips) > 0:
            warnings.append(f"⚠️  Contains Session + User + IP - COMPLETE CHAIN IN ONE DOC!")
        
        # Log warnings
        if warnings:
            logger.error(f"   🚨 CONTAINMENT VIOLATION in {doc_plan.doc_id}:")
            for warning in warnings:
                logger.error(f"      {warning}")
            logger.error(f"      This document reveals too much! Should be split into multiple docs.")
            logger.error(f"      Single-LLM will likely solve this mystery easily!")
        
        return len(warnings) == 0

