"""Step 4: Document Planning - distribute clues across documents."""

import logging
from typing import List, Dict, Any
from narrative.graph import Character, TimelineEvent, Location, DocumentPlan, ClueAssignment
from .clue_fragmenter import ClueFragmenter, ClueFragment


logger = logging.getLogger(__name__)


DOCUMENT_PLANNING_PROMPT = """You are planning which documents to generate for a detective mystery.

COMPLETE CONTEXT:

CHARACTERS:
{characters_summary}

TIMELINE:
{timeline_summary}

LOCATIONS:
{locations_summary}

PROOF TREE - CLUES THAT MUST BE INCLUDED:
{proof_tree_clues}

YOUR TASK:
Plan exactly {num_documents} documents that will contain the mystery clues.

AVAILABLE DOCUMENT TYPES:
- email: Email correspondence
- diary: Personal diary entry
- police_report: Official police documentation
- badge_log: Physical access logs
- witness_statement: Witness testimony
- bank_statement: Financial transaction records
- newspaper: News article
- internal_memo: Internal company memo
- phone_record: Call logs
- receipt: Purchase receipt
- surveillance_log: Security monitoring log
- medical_record: Medical documentation

For each document specify:
- doc_id: Unique ID like "doc_1_email_classified"
- doc_type: One of the types above
- author: Which character created it (or "system" for automated logs like badge_log)
- timestamp: When created (ISO format, must fit timeline)
- clues_to_include: Array of clue assignments
  Each clue: {{"clue_id": "unique_id", "clue_data": "exact data to include", "field_to_insert": "field_name", "importance": "key|supporting|red_herring"}}
- purpose: Why this document exists narratively (1-2 sentences)
- is_red_herring: true/false ({num_red_herrings} documents should be red herrings)

🚨 CRITICAL RULES FOR MULTI-HOP REASONING:

1. **FRAGMENT CLUES ACROSS DOCUMENTS** - Each document should contain ONLY ONE small piece!
   ❌ BAD: "User ID 'jsmith' logged in from IP 192.168.1.42 at 2:30 AM"
   ✅ GOOD (in separate documents):
      - Doc A: "IP 192.168.1.42 accessed server at 2:30 AM"
      - Doc B: "VPN session #12345 from IP 192.168.1.42"
      - Doc C: "User jsmith initiated VPN session #12345"

2. **NO DIRECT CONNECTIONS** - Don't put connected clues in the same document!
   ❌ BAD: Single doc says "User jsmith (Badge #123) accessed at 2:30 AM"
   ✅ GOOD: Split into 3 docs:
      - Doc 1: "Badge #123 scanned at 2:30 AM"
      - Doc 2: "User jsmith logged in at 2:29 AM"  
      - Doc 3: "Employee records: jsmith has badge #123"

3. **USE INTERMEDIATE IDs** - Force connections through technical identifiers!
   Examples: Session IDs, Transaction IDs, Request IDs, Ticket Numbers
   ❌ BAD: "User jsmith deleted files"
   ✅ GOOD: "Request #AB123 deleted files" + (elsewhere) "jsmith submitted request #AB123"

4. **ONLY RAW EVIDENCE** - Never state conclusions or final answer
   ❌ BAD: "John Smith deleted the files" (conclusion!)
   ✅ GOOD: "User ID 'jsmith' in deletion log" (evidence fragment)

Output ONLY valid JSON:
{{
  "document_plan": [
    {{
      "doc_id": "doc_1_badge_scan",
      "doc_type": "badge_log",
      "author": "system",
      "timestamp": "2024-11-10T14:30:00Z",
      "clues_to_include": [
        {{
          "clue_id": "badge_scan",
          "clue_data": "Badge #45123 scanned at server room entrance",
          "field_to_insert": "entries",
          "importance": "key"
        }}
      ],
      "purpose": "Physical access log showing badge usage",
      "is_red_herring": false
    }}
  ]
}}"""


class DocumentPlanner:
    """Plan document types and clue distribution using LLM."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.fragmenter = ClueFragmenter()
    
    async def plan_documents(
        self,
        characters: List[Character],
        timeline: List[TimelineEvent],
        locations: List[Location],
        proof_tree: Dict[str, Any],
        num_documents: int,
        config: Dict[str, Any]
    ) -> List[DocumentPlan]:
        """
        Plan document generation and clue distribution.
        
        Args:
            characters: Characters from Step 1
            timeline: Timeline from Step 2
            locations: Locations from Step 3
            proof_tree: Proof tree with clues
            num_documents: Target number of documents
            config: Configuration
        
        Returns:
            List of DocumentPlan objects
        """
        logger.info("📄 Step 4: Planning documents...")
        
        # Calculate red herrings (20-30% of documents)
        num_red_herrings = max(2, int(num_documents * 0.25))
        
        # Build prompt
        prompt = self._build_prompt(
            characters,
            timeline,
            locations,
            proof_tree,
            num_documents,
            num_red_herrings
        )
        
        # Generate with LLM
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.6),
                max_tokens=config.get("max_tokens", 4000)
            )
            
            # Parse document plans
            doc_plans = []
            for doc_data in response.get("document_plan", []):
                # Parse clues
                clues = [
                    ClueAssignment.from_dict(clue)
                    for clue in doc_data.get("clues_to_include", [])
                ]
                
                doc_plan = DocumentPlan(
                    doc_id=doc_data["doc_id"],
                    doc_type=doc_data["doc_type"],
                    author=doc_data["author"],
                    timestamp=doc_data["timestamp"],
                    clues_to_include=clues,
                    purpose=doc_data.get("purpose", ""),
                    is_red_herring=doc_data.get("is_red_herring", False),
                    references=[]  # Will be filled in Step 5
                )
                doc_plans.append(doc_plan)
            
            # Validate
            self._validate_document_plan(doc_plans, proof_tree, num_documents)
            
            # Validate clue/document type matches
            logger.info("   🔍 Validating clue-document type compatibility...")
            for doc_plan in doc_plans:
                self._validate_clue_document_type_match(doc_plan)
            
            logger.info(f"   ✅ Planned {len(doc_plans)} documents")
            
            # Log distribution
            doc_types = {}
            for doc in doc_plans:
                doc_types[doc.doc_type] = doc_types.get(doc.doc_type, 0) + 1
            
            for doc_type, count in sorted(doc_types.items()):
                logger.info(f"      - {count}x {doc_type}")
            
            red_herring_count = sum(1 for doc in doc_plans if doc.is_red_herring)
            logger.info(f"      - {red_herring_count} red herrings")
            
            return doc_plans
        
        except Exception as e:
            logger.error(f"   ❌ Document planning failed: {e}")
            raise
    
    def _build_prompt(
        self,
        characters: List[Character],
        timeline: List[TimelineEvent],
        locations: List[Location],
        proof_tree: Dict[str, Any],
        num_documents: int,
        num_red_herrings: int
    ) -> str:
        """Build the document planning prompt."""
        
        # Summarize context
        characters_summary = "\n".join([
            f"- {char.name} ({char.role})"
            for char in characters
        ])
        
        timeline_summary = "\n".join([
            f"- {event.timestamp[:16]}: {event.event_type} at {event.location}"
            for event in timeline[:12]
        ])
        if len(timeline) > 12:
            timeline_summary += f"\n... and {len(timeline) - 12} more events"
        
        locations_summary = "\n".join([
            f"- {loc.name} ({loc.type})"
            for loc in locations
        ])
        
        # Extract clues from proof tree
        proof_tree_clues = self._extract_clues_from_proof_tree(proof_tree)
        
        # Fill prompt template
        prompt = DOCUMENT_PLANNING_PROMPT.format(
            characters_summary=characters_summary,
            timeline_summary=timeline_summary,
            locations_summary=locations_summary,
            proof_tree_clues=proof_tree_clues,
            num_documents=num_documents,
            num_red_herrings=num_red_herrings
        )
        
        return prompt
    
    def _extract_clues_from_proof_tree(self, proof_tree: Dict[str, Any]) -> str:
        """
        Extract ONLY raw evidence clues (no conclusions).
        
        Since the proof tree should already generate ATOMIC clues (one identifier per node),
        we just pass them through with a warning to keep them separate!
        """
        nodes = proof_tree.get("inference_nodes", [])
        
        if not nodes:
            return "- Clue 1: Evidence of meeting time\n- Clue 2: Badge access records\n- Clue 3: Financial transaction"
        
        clues = []
        clue_id = 1
        
        for node in nodes:
            inference = node.get("inference", "")
            document_ids = node.get("document_ids", [])
            parent_nodes = node.get("parent_nodes", [])
            
            # CRITICAL: Only include evidence-level nodes (no parents)
            # Skip conclusion nodes - the LLM must derive these!
            if parent_nodes:
                logger.info(f"   📍 Skipping conclusion node: {inference} (must be derived from evidence)")
                continue
            
            # Each evidence node should already be ATOMIC
            # Just pass it through with a strong warning
            clue_desc = f"Clue {clue_id}: {inference}"
            clue_desc += "\n   ⚠️  THIS CLUE MUST BE IN ITS OWN DOCUMENT!"
            clue_desc += "\n   ⚠️  DO NOT combine with other clues!"
            
            clues.append(clue_desc)
            clue_id += 1
        
        if not clues:
            logger.warning("   ⚠️  No evidence-level clues found in proof tree!")
            return "- Clue 1: Raw evidence must be included in documents"
        
        return "\n\n- ".join([""] + clues)
    
    def _validate_clue_document_type_match(self, doc_plan: DocumentPlan):
        """Validate that clues match the document type."""
        doc_type = doc_plan.doc_type
        clues_text = " ".join([c.clue_data.lower() for c in doc_plan.clues_to_include])
        
        # Define what each document type should contain
        type_keywords = {
            "badge_log": ["badge", "access", "entry", "scan", "door", "location", "swipe"],
            "email": ["sent", "received", "message", "reply", "attachment", "subject"],
            "internal_memo": ["policy", "announcement", "directive", "procedure"],
            "police_report": ["incident", "investigation", "evidence", "witness", "case"],
            "surveillance_log": ["camera", "footage", "observation", "monitor", "security"],
            "bank_statement": ["transaction", "payment", "deposit", "withdrawal", "account"],
            "phone_record": ["call", "phone", "number", "duration", "contact"],
            "witness_statement": ["saw", "heard", "observed", "testified", "statement"],
            "receipt": ["purchased", "item", "merchant", "payment", "total"],
            "diary": ["personal", "feeling", "thought", "dear diary", "private"]
        }
        
        # Check for INCOMPATIBLE clues
        incompatible = {
            "badge_log": ["expense", "approved", "payment", "transaction", "claim", "reimbursement"],
            "email": ["badge scan", "physical access"],
            "bank_statement": ["badge", "camera", "footage"]
        }
        
        # Check if clues mention things this document type should NOT contain
        if doc_type in incompatible:
            for bad_keyword in incompatible[doc_type]:
                if bad_keyword in clues_text:
                    logger.error(f"   🚨 TYPE MISMATCH: {doc_type} should NOT contain '{bad_keyword}'!")
                    logger.error(f"      Clue: {clues_text[:100]}")
                    logger.error(f"      This will cause multi-hop validation to fail!")
                    return False
        
        return True
    
    def _validate_document_plan(
        self,
        doc_plans: List[DocumentPlan],
        proof_tree: Dict[str, Any],
        requested_docs: int
    ):
        """Validate document plan."""
        if not doc_plans:
            raise ValueError("No documents planned")
        
        # Allow 80% of requested documents (LLMs sometimes generate slightly fewer)
        min_docs = max(5, int(requested_docs * 0.8))
        if len(doc_plans) < min_docs:
            raise ValueError(f"Too few documents: {len(doc_plans)} (minimum {min_docs}, requested {requested_docs})")
        
        # Check for duplicate IDs
        doc_ids = [doc.doc_id for doc in doc_plans]
        if len(doc_ids) != len(set(doc_ids)):
            raise ValueError("Duplicate document IDs detected")
        
        # Verify at least some clues are distributed
        total_clues = sum(len(doc.clues_to_include) for doc in doc_plans)
        if total_clues == 0:
            logger.warning("   ⚠️  No clues assigned to documents")
