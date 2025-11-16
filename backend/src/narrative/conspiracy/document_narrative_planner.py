"""
Document Narrative Planner

Creates complete narrative blueprints for documents before generation.
This is the intelligence layer that decides what content goes where.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.conspiracy import SubGraph, MysteryAnswer, ConspiracyPremise
from .evidence_fact_extractor import AtomicFact, EvidenceFactExtractor
from .political_context_generator import PoliticalContext
import random
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentNarrativePlan:
    """
    Complete blueprint for one document.
    Contains all information needed for rendering.
    """
    document_id: str
    document_type: str  # "security_log", "email", "performance_review", etc.
    
    # Narrative structure
    narrative_purpose: str
    # e.g., "Show suspicious late-night access pattern"
    
    narrative_setting: str
    # e.g., "Building 7 security checkpoint, night shift"
    
    # Facts to embed (from evidence chains)
    required_facts: List[AtomicFact] = field(default_factory=list)
    
    # Cross-chain connections
    connected_chains: List[str] = field(default_factory=list)
    
    # Narrative framing
    narrative_tone: str = "neutral"
    # e.g., "routine_bureaucratic", "concerned_informal", "technical_encrypted"
    
    perspective: str = "third_person"
    # e.g., "automated_system", "concerned_colleague", "security_officer"
    
    def __repr__(self):
        return f"<DocumentPlan {self.document_id}: {self.document_type} with {len(self.required_facts)} facts>"


class DocumentNarrativePlanner:
    """
    Creates complete narrative plans for all documents.
    
    This layer has ALL the intelligence:
    - What facts go where
    - How narratives connect
    - Answer containment enforcement
    - Cross-chain document design
    """
    
    # Document type templates
    DOCUMENT_TYPES = [
        "security_access_log",
        "internal_email",
        "performance_review",
        "encrypted_message",
        "meeting_notes",
        "financial_record",
        "system_log",
        "personnel_file",
        "incident_report",
        "research_log"
    ]
    
    def __init__(self, llm_client):
        """Initialize with LLM client for fact extraction."""
        self.llm = llm_client
        self.fact_extractor = EvidenceFactExtractor(llm_client)
    
    async def create_narrative_plans(
        self,
        subgraphs: List[SubGraph],
        answer_template: MysteryAnswer,
        characters: List[Dict],
        political_context: PoliticalContext,
        premise: ConspiracyPremise,
        num_documents: int,
        difficulty: str
    ) -> List[DocumentNarrativePlan]:
        """
        Main planning function - creates complete narrative blueprints.
        
        Steps:
        1. Extract all atomic facts from evidence chains (with LLM)
        2. Determine document types and purposes
        3. Assign facts to documents (with containment)
        4. Design cross-chain connections
        5. Create narrative blueprints
        """
        logger.info(f"Creating narrative plans for {num_documents} documents")
        
        # Step 1: Extract all facts (async with LLM)
        all_facts = await self.fact_extractor.extract_all_facts(subgraphs, answer_template)
        logger.info(f"  Extracted {len(all_facts)} atomic facts")
        
        # Step 2: Design document purposes
        doc_purposes = self._design_document_purposes(
            num_documents,
            subgraphs,
            difficulty,
            political_context,
            premise
        )
        logger.info(f"  Designed {len(doc_purposes)} document purposes")
        
        # Step 3: Assign facts to documents with containment
        self._assign_facts_to_documents(
            doc_purposes,
            all_facts,
            subgraphs,
            answer_template
        )
        logger.info(f"  Assigned facts to documents with containment")
        
        # Step 4: Design cross-chain connections
        self._design_cross_chain_documents(doc_purposes, subgraphs)
        logger.info(f"  Designed cross-chain connections")
        
        # Step 5: Finalize narrative details
        self._finalize_narrative_details(doc_purposes, characters, political_context)
        logger.info(f"  Finalized narrative details")
        
        # Log containment stats
        self._log_containment_stats(doc_purposes)
        
        return doc_purposes
    
    def _design_document_purposes(
        self,
        num_documents: int,
        subgraphs: List[SubGraph],
        difficulty: str,
        political_context: PoliticalContext,
        premise: ConspiracyPremise
    ) -> List[DocumentNarrativePlan]:
        """
        Design the narrative purpose for each document.
        
        Creates a mix of document types that align with evidence chains.
        """
        plans = []
        
        # Categorize subgraphs by type
        identity_chains = [sg for sg in subgraphs if sg.subgraph_type.value == "identity"]
        psychological_chains = [sg for sg in subgraphs if sg.subgraph_type.value == "psychological"]
        crypto_chains = [sg for sg in subgraphs if sg.subgraph_type.value == "crypto"]
        
        # Calculate document distribution
        num_identity_docs = max(3, len(identity_chains) * 2)
        num_psychological_docs = max(2, len(psychological_chains) * 2)
        num_crypto_docs = max(2, len(crypto_chains))
        
        # Normalize to num_documents
        total_planned = num_identity_docs + num_psychological_docs + num_crypto_docs
        if total_planned > num_documents:
            scale = num_documents / total_planned
            num_identity_docs = int(num_identity_docs * scale)
            num_psychological_docs = int(num_psychological_docs * scale)
            num_crypto_docs = num_documents - num_identity_docs - num_psychological_docs
        
        doc_id = 0
        
        # Create identity-focused documents
        for i in range(num_identity_docs):
            plan = self._create_identity_document_plan(doc_id, identity_chains, political_context)
            plans.append(plan)
            doc_id += 1
        
        # Create psychological-focused documents
        for i in range(num_psychological_docs):
            plan = self._create_psychological_document_plan(doc_id, psychological_chains, political_context)
            plans.append(plan)
            doc_id += 1
        
        # Create crypto-focused documents
        for i in range(num_crypto_docs):
            plan = self._create_crypto_document_plan(doc_id, crypto_chains, political_context)
            plans.append(plan)
            doc_id += 1
        
        # Fill remaining slots if we're under target
        while len(plans) < num_documents:
            # Create additional mixed-type documents
            if identity_chains:
                plan = self._create_identity_document_plan(doc_id, identity_chains, political_context)
            elif psychological_chains:
                plan = self._create_psychological_document_plan(doc_id, psychological_chains, political_context)
            elif crypto_chains:
                plan = self._create_crypto_document_plan(doc_id, crypto_chains, political_context)
            else:
                # Fallback: create generic document
                plan = self._create_identity_document_plan(doc_id, [], political_context)
            
            plans.append(plan)
            doc_id += 1
        
        return plans
    
    def _create_identity_document_plan(
        self,
        doc_id: int,
        identity_chains: List[SubGraph],
        political_context: PoliticalContext
    ) -> DocumentNarrativePlan:
        """Create a document plan focused on identity evidence."""
        doc_type = random.choice([
            "security_access_log",
            "system_log",
            "personnel_file",
            "incident_report"
        ])
        
        purposes = [
            "Reveal suspicious access patterns and credentials",
            "Document network activity and system usage",
            "Record personnel movements and badge usage",
            "Track authentication attempts and timestamps"
        ]
        
        # Get organization name for settings
        org_name = "the organization"
        if political_context.shadow_agencies:
            org_name = political_context.shadow_agencies[0].get("name", "the organization")
        
        settings = [
            f"Security checkpoint in {org_name} headquarters",
            f"Network operations center monitoring system",
            f"Personnel database and access control system",
            f"Building security infrastructure"
        ]
        
        return DocumentNarrativePlan(
            document_id=f"doc_{doc_id:03d}",
            document_type=doc_type,
            narrative_purpose=random.choice(purposes),
            narrative_setting=random.choice(settings),
            connected_chains=[chain.subgraph_id for chain in identity_chains] if identity_chains else [],
            narrative_tone="routine_bureaucratic",
            perspective="automated_system"
        )
    
    def _create_psychological_document_plan(
        self,
        doc_id: int,
        psychological_chains: List[SubGraph],
        political_context: PoliticalContext
    ) -> DocumentNarrativePlan:
        """Create a document plan focused on psychological evidence."""
        doc_type = random.choice([
            "internal_email",
            "performance_review",
            "meeting_notes",
            "personnel_file"
        ])
        
        purposes = [
            "Document behavioral changes and concerning patterns",
            "Record colleague observations and concerns",
            "Capture unusual dedication or obsession with work",
            "Note personality shifts and motivational changes"
        ]
        
        # Get organization name for settings
        org_name = "the organization"
        if political_context.shadow_agencies:
            org_name = political_context.shadow_agencies[0].get("name", "the organization")
        
        settings = [
            f"Internal communications within {org_name}",
            f"HR department performance evaluation",
            f"Team meeting discussions and observations",
            f"Personnel management records"
        ]
        
        return DocumentNarrativePlan(
            document_id=f"doc_{doc_id:03d}",
            document_type=doc_type,
            narrative_purpose=random.choice(purposes),
            narrative_setting=random.choice(settings),
            connected_chains=[chain.subgraph_id for chain in psychological_chains] if psychological_chains else [],
            narrative_tone="concerned_informal",
            perspective="colleague_observer"
        )
    
    def _create_crypto_document_plan(
        self,
        doc_id: int,
        crypto_chains: List[SubGraph],
        political_context: PoliticalContext
    ) -> DocumentNarrativePlan:
        """Create a document plan focused on cryptographic evidence."""
        doc_type = random.choice([
            "encrypted_message",
            "system_log",
            "research_log"
        ])
        
        purposes = [
            "Contain encrypted operational communications",
            "Record secure transmission of sensitive information",
            "Document classified research and experiments",
            "Store encoded mission parameters and objectives"
        ]
        
        # Get organization name for settings
        org_name = "the organization"
        if political_context.shadow_agencies:
            org_name = political_context.shadow_agencies[0].get("name", "the organization")
        
        settings = [
            f"Secure communications channel for {org_name}",
            f"Encrypted network traffic logs",
            f"Classified research facility documentation",
            f"Secure operational command system"
        ]
        
        return DocumentNarrativePlan(
            document_id=f"doc_{doc_id:03d}",
            document_type=doc_type,
            narrative_purpose=random.choice(purposes),
            narrative_setting=random.choice(settings),
            connected_chains=[chain.subgraph_id for chain in crypto_chains] if crypto_chains else [],
            narrative_tone="technical_encrypted",
            perspective="secure_system"
        )
    
    def _assign_facts_to_documents(
        self,
        doc_plans: List[DocumentNarrativePlan],
        all_facts: List[AtomicFact],
        subgraphs: List[SubGraph],
        answer_template: MysteryAnswer
    ):
        """
        Assign facts to documents with containment enforcement.
        
        CRITICAL CONTAINMENT RULES:
        - WHO answer (name): Only in 2-3 documents
        - WHAT answer (codename): Only in 1 document
        - WHY answer (phrase): Only in 2-3 documents
        - HOW answer (method): Only in 1-2 documents
        """
        # Group facts by chain
        facts_by_chain = {}
        for fact in all_facts:
            if fact.source_chain not in facts_by_chain:
                facts_by_chain[fact.source_chain] = []
            facts_by_chain[fact.source_chain].append(fact)
        
        # Separate answer-critical facts
        who_facts = [f for f in all_facts if f.answer_dimension == "who"]
        what_facts = [f for f in all_facts if f.answer_dimension == "what"]
        why_facts = [f for f in all_facts if f.answer_dimension == "why"]
        how_facts = [f for f in all_facts if f.answer_dimension == "how"]
        
        # Apply containment for each answer dimension
        self._apply_who_containment(doc_plans, who_facts, facts_by_chain, max_docs=3)
        self._apply_what_containment(doc_plans, what_facts, facts_by_chain, max_docs=1)
        self._apply_why_containment(doc_plans, why_facts, facts_by_chain, max_docs=3)
        self._apply_how_containment(doc_plans, how_facts, facts_by_chain, max_docs=2)
        
        # Assign non-answer facts to all relevant documents
        self._assign_supporting_facts(doc_plans, all_facts, facts_by_chain)
    
    def _apply_who_containment(
        self,
        doc_plans: List[DocumentNarrativePlan],
        who_facts: List[AtomicFact],
        facts_by_chain: Dict[str, List[AtomicFact]],
        max_docs: int
    ):
        """Contain WHO answer to max_docs documents."""
        if not who_facts:
            return
        
        who_fact = who_facts[0]  # Primary WHO answer
        
        # Find documents connected to WHO chain
        eligible_docs = [
            plan for plan in doc_plans
            if who_fact.source_chain in plan.connected_chains
        ]
        
        if not eligible_docs:
            # If no eligible docs, use any identity-focused documents
            eligible_docs = [
                plan for plan in doc_plans
                if "security" in plan.document_type or "personnel" in plan.document_type
            ]
        
        # Select max_docs to contain the WHO answer
        selected_docs = random.sample(eligible_docs, min(max_docs, len(eligible_docs)))
        
        for doc in selected_docs:
            doc.required_facts.append(who_fact)
        
        logger.info(f"  WHO answer '{who_fact.value}' assigned to {len(selected_docs)} documents")
    
    def _apply_what_containment(
        self,
        doc_plans: List[DocumentNarrativePlan],
        what_facts: List[AtomicFact],
        facts_by_chain: Dict[str, List[AtomicFact]],
        max_docs: int
    ):
        """Contain WHAT answer to max_docs documents."""
        if not what_facts:
            return
        
        what_fact = what_facts[0]  # Primary WHAT answer
        
        # Find documents connected to WHAT chain (crypto)
        eligible_docs = [
            plan for plan in doc_plans
            if what_fact.source_chain in plan.connected_chains
        ]
        
        if not eligible_docs:
            # Use crypto-focused documents
            eligible_docs = [
                plan for plan in doc_plans
                if "encrypted" in plan.document_type or plan.narrative_tone == "technical_encrypted"
            ]
        
        # Select ONLY max_docs (usually 1) to contain the WHAT answer
        selected_docs = random.sample(eligible_docs, min(max_docs, len(eligible_docs)))
        
        for doc in selected_docs:
            doc.required_facts.append(what_fact)
        
        logger.info(f"  WHAT answer '{what_fact.value}' assigned to {len(selected_docs)} documents")
    
    def _apply_why_containment(
        self,
        doc_plans: List[DocumentNarrativePlan],
        why_facts: List[AtomicFact],
        facts_by_chain: Dict[str, List[AtomicFact]],
        max_docs: int
    ):
        """Contain WHY answer to max_docs documents."""
        if not why_facts:
            return
        
        why_fact = why_facts[0]  # Primary WHY answer
        
        # Find documents connected to WHY chain (psychological)
        eligible_docs = [
            plan for plan in doc_plans
            if why_fact.source_chain in plan.connected_chains
        ]
        
        if not eligible_docs:
            # Use psychological-focused documents
            eligible_docs = [
                plan for plan in doc_plans
                if "email" in plan.document_type or "meeting" in plan.document_type
            ]
        
        # Select max_docs to contain the WHY answer
        selected_docs = random.sample(eligible_docs, min(max_docs, len(eligible_docs)))
        
        for doc in selected_docs:
            doc.required_facts.append(why_fact)
        
        logger.info(f"  WHY answer '{why_fact.value}' assigned to {len(selected_docs)} documents")
    
    def _apply_how_containment(
        self,
        doc_plans: List[DocumentNarrativePlan],
        how_facts: List[AtomicFact],
        facts_by_chain: Dict[str, List[AtomicFact]],
        max_docs: int
    ):
        """Contain HOW answer to max_docs documents."""
        if not how_facts:
            return
        
        how_fact = how_facts[0]  # Primary HOW answer
        
        # Find documents connected to HOW chain (crypto)
        eligible_docs = [
            plan for plan in doc_plans
            if how_fact.source_chain in plan.connected_chains
        ]
        
        if not eligible_docs:
            # Use crypto-focused documents
            eligible_docs = [
                plan for plan in doc_plans
                if "encrypted" in plan.document_type or plan.narrative_tone == "technical_encrypted"
            ]
        
        # Select max_docs to contain the HOW answer
        selected_docs = random.sample(eligible_docs, min(max_docs, len(eligible_docs)))
        
        for doc in selected_docs:
            doc.required_facts.append(how_fact)
        
        logger.info(f"  HOW answer '{how_fact.value}' assigned to {len(selected_docs)} documents")
    
    def _assign_supporting_facts(
        self,
        doc_plans: List[DocumentNarrativePlan],
        all_facts: List[AtomicFact],
        facts_by_chain: Dict[str, List[AtomicFact]]
    ):
        """
        Assign non-answer facts to documents.
        These provide context and help create the evidence network.
        
        CRITICAL: Keep fact count LOW to avoid bloated documents!
        """
        MAX_FACTS_PER_DOC = 6  # Hard cap to prevent bloat
        
        for doc_plan in doc_plans:
            # Get all facts from connected chains
            for chain_id in doc_plan.connected_chains:
                if chain_id in facts_by_chain:
                    chain_facts = facts_by_chain[chain_id]
                    
                    # Add non-answer facts (if not already added)
                    for fact in chain_facts:
                        if not fact.is_answer_critical and fact not in doc_plan.required_facts:
                            # REDUCED probability and hard cap to prevent bloat
                            if len(doc_plan.required_facts) < MAX_FACTS_PER_DOC and random.random() < 0.3:  # Only 30% chance
                                doc_plan.required_facts.append(fact)
    
    def _design_cross_chain_documents(
        self,
        doc_plans: List[DocumentNarrativePlan],
        subgraphs: List[SubGraph]
    ):
        """
        Design documents that connect multiple chains.
        This creates the multi-hop network effect.
        """
        # Identify chain types
        identity_chains = [sg.subgraph_id for sg in subgraphs if sg.subgraph_type.value == "identity"]
        psychological_chains = [sg.subgraph_id for sg in subgraphs if sg.subgraph_type.value == "psychological"]
        crypto_chains = [sg.subgraph_id for sg in subgraphs if sg.subgraph_type.value == "crypto"]
        
        # Create cross-chain connections
        num_cross_chain = max(3, len(doc_plans) // 4)  # 25% of documents
        
        for i in range(num_cross_chain):
            if i < len(doc_plans):
                doc = doc_plans[i]
                
                # Connect identity + psychological
                if identity_chains and psychological_chains:
                    if random.random() < 0.5:
                        doc.connected_chains.append(random.choice(psychological_chains))
                
                # Connect identity + crypto
                if identity_chains and crypto_chains:
                    if random.random() < 0.3:
                        doc.connected_chains.append(random.choice(crypto_chains))
        
        logger.info(f"  Created cross-chain connections in {num_cross_chain} documents")
    
    def _finalize_narrative_details(
        self,
        doc_plans: List[DocumentNarrativePlan],
        characters: List[Dict],
        political_context: PoliticalContext
    ):
        """
        Finalize narrative details for all documents.
        """
        # This is where we could add more sophisticated narrative design
        # For now, the basic structure is already set
        pass
    
    def _log_containment_stats(self, doc_plans: List[DocumentNarrativePlan]):
        """Log containment statistics."""
        who_docs = sum(1 for plan in doc_plans 
                       if any(f.answer_dimension == "who" for f in plan.required_facts))
        what_docs = sum(1 for plan in doc_plans 
                        if any(f.answer_dimension == "what" for f in plan.required_facts))
        why_docs = sum(1 for plan in doc_plans 
                       if any(f.answer_dimension == "why" for f in plan.required_facts))
        how_docs = sum(1 for plan in doc_plans 
                       if any(f.answer_dimension == "how" for f in plan.required_facts))
        
        logger.info(f"  Containment Stats:")
        logger.info(f"    WHO answer in {who_docs} documents")
        logger.info(f"    WHAT answer in {what_docs} documents")
        logger.info(f"    WHY answer in {why_docs} documents")
        logger.info(f"    HOW answer in {how_docs} documents")

