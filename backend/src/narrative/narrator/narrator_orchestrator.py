"""Narrator Orchestrator - runs all 5 steps to build narrative graph."""

import logging
from typing import Dict, Any
from ..graph import NarrativeGraph
from .step_minus1_premise import PremiseGenerator
from .step0_proof_tree import ProofTreeGenerator
from .step1_characters import CharacterGenerator
from .step2_timeline import TimelineGenerator
from .step3_locations import LocationGenerator
from .step4_document_plan import DocumentPlanner
from .step5_graph_assembly import GraphAssembler


logger = logging.getLogger(__name__)


class NarratorOrchestrator:
    """
    Orchestrates the 7-step narrator process to build complete narrative graph.
    
    Steps:
    -1. Generate mystery premise (question + answer)
    0. Generate proof tree (multi-hop reasoning structure)
    1. Generate characters
    2. Generate timeline  
    3. Generate locations
    4. Plan documents and distribute clues
    5. Assemble document reference graph
    """
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        """
        Initialize orchestrator.
        
        Args:
            llm_client: LLM client for generation
            config: Configuration dictionary
        """
        self.llm = llm_client
        self.config = config
        
        # Initialize all step generators
        self.premise_gen = PremiseGenerator(llm_client)
        self.proof_gen = ProofTreeGenerator(llm_client)
        self.char_gen = CharacterGenerator(llm_client)
        self.timeline_gen = TimelineGenerator(llm_client)
        self.location_gen = LocationGenerator(llm_client)
        self.doc_planner = DocumentPlanner(llm_client)
        self.graph_assembler = GraphAssembler(llm_client)
    
    async def build_narrative_graph(
        self,
        mystery_question: str = None,
        mystery_answer: str = None,
        difficulty: int = 5,
        num_documents: int = 20,
        proof_tree: Dict[str, Any] = None
    ) -> tuple[NarrativeGraph, Dict[str, Any], str, str]:
        """
        Run all narrator steps to build complete narrative graph.
        
        Args:
            mystery_question: The mystery question (will generate if None)
            mystery_answer: The answer to the mystery (will generate if None)
            difficulty: Difficulty level (1-10)
            num_documents: Target number of documents
            proof_tree: Optional pre-generated proof tree (will generate if None)
        
        Returns:
            Tuple of (NarrativeGraph, proof_tree, question, answer)
        """
        logger.info("="*60)
        logger.info("🎭 STARTING NARRATIVE GENERATION")
        logger.info("="*60)
        logger.info(f"Difficulty: {difficulty}/10")
        logger.info(f"Target Documents: {num_documents}")
        logger.info("")
        
        # STEP -1: Generate Premise (if not provided)
        if not mystery_question or not mystery_answer:
            logger.info("STEP -1/5: PREMISE GENERATION")
            logger.info("-" * 60)
            mystery_question, mystery_answer = await self.premise_gen.generate_premise(
                difficulty=difficulty,
                config=self.config
            )
        else:
            logger.info("STEP -1/5: Using provided premise")
            logger.info(f"   Question: {mystery_question}")
            logger.info(f"   Answer: {mystery_answer}")
            logger.info("")
        
        # Mystery context for all steps
        mystery_context = {
            "question": mystery_question,
            "answer": mystery_answer,
            "difficulty": difficulty,
            "setting": self.config.get("setting", "corporate office"),
            "time_period": self.config.get("time_period", "modern day")
        }
        
        # STEP 0: Generate Proof Tree (if not provided)
        if proof_tree is None:
            logger.info("STEP 0/5: PROOF TREE GENERATION")
            logger.info("-" * 60)
            proof_tree = await self.proof_gen.generate_proof_tree(
                question=mystery_question,
                answer=mystery_answer,
                difficulty=difficulty,
                config=self.config.get("step0_proof_tree", {})
            )
            logger.info("")
        else:
            logger.info("STEP 0/5: Using pre-generated proof tree")
            logger.info("")
        
        # STEP 1: Generate Characters
        logger.info("STEP 1/5: CHARACTER GENERATION")
        logger.info("-" * 60)
        characters = await self.char_gen.generate_characters(
            mystery_context=mystery_context,
            proof_tree=proof_tree,
            config=self.config.get("step1_characters", {})
        )
        logger.info("")
        
        # STEP 2: Generate Timeline
        logger.info("STEP 2/5: TIMELINE GENERATION")
        logger.info("-" * 60)
        timeline = await self.timeline_gen.generate_timeline(
            characters=characters,
            mystery_context=mystery_context,
            proof_tree=proof_tree,
            config=self.config.get("step2_timeline", {})
        )
        logger.info("")
        
        # STEP 3: Generate Locations
        logger.info("STEP 3/5: LOCATION GENERATION")
        logger.info("-" * 60)
        locations = await self.location_gen.generate_locations(
            characters=characters,
            timeline=timeline,
            config=self.config.get("step3_locations", {})
        )
        logger.info("")
        
        # STEP 4: Plan Documents
        logger.info("STEP 4/5: DOCUMENT PLANNING")
        logger.info("-" * 60)
        document_plan = await self.doc_planner.plan_documents(
            characters=characters,
            timeline=timeline,
            locations=locations,
            proof_tree=proof_tree,
            num_documents=num_documents,
            config=self.config.get("step4_document_plan", {})
        )
        logger.info("")
        
        # STEP 5: Assemble Graph
        logger.info("STEP 5/5: GRAPH ASSEMBLY")
        logger.info("-" * 60)
        document_plan = await self.graph_assembler.assemble_graph(
            document_plan=document_plan,
            characters=characters,
            timeline=timeline,
            mystery_context=mystery_context,
            config=self.config.get("step5_graph_assembly", {})
        )
        logger.info("")
        
        # BUILD FINAL NARRATIVE GRAPH
        logger.info("="*60)
        logger.info("✅ NARRATIVE GRAPH COMPLETE")
        logger.info("="*60)
        
        narrative_graph = NarrativeGraph(
            mystery_question=mystery_question,
            mystery_answer=mystery_answer,
            difficulty=difficulty,
            characters=characters,
            timeline=timeline,
            locations=locations,
            document_plan=document_plan
        )
        
        # Log final statistics
        logger.info(f"Final Statistics:")
        logger.info(f"  - Characters: {len(characters)}")
        logger.info(f"  - Timeline Events: {len(timeline)}")
        logger.info(f"  - Locations: {len(locations)}")
        logger.info(f"  - Documents Planned: {len(document_plan)}")
        
        total_clues = sum(len(doc.clues_to_include) for doc in document_plan)
        logger.info(f"  - Total Clues: {total_clues}")
        
        total_refs = sum(len(doc.references) for doc in document_plan)
        logger.info(f"  - Document References: {total_refs}")
        
        logger.info("")
        logger.info("Ready for document generation phase!")
        logger.info("")
        
        return narrative_graph, proof_tree, mystery_question, mystery_answer

