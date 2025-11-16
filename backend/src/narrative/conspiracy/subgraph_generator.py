"""Sub-Graph Generator - creates multiple evidence chains (cadavre exquis)."""

import logging
import random
from typing import List, Dict, Any
from models.conspiracy import (
    ConspiracyPremise,
    PoliticalContext,
    SubGraph,
    EvidenceNode,
    InferenceNode,
    EvidenceType,
    AnswerDimension
)
from .subgraph_types import get_architecture_for_type, SubGraphArchitecture


logger = logging.getLogger(__name__)


class SubGraphGenerator:
    """Generate multiple independent sub-graphs (evidence chains)."""
    
    def __init__(self):
        """Initialize generator."""
        pass
    
    def generate_subgraphs(
        self,
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        difficulty: int = 5,
        num_documents: int = 20
    ) -> List[SubGraph]:
        """
        Generate multiple sub-graphs for the conspiracy.
        
        Args:
            premise: Conspiracy premise with 4 answers
            political_context: Political backdrop
            difficulty: Complexity level (1-10)
            num_documents: Target number of documents (influences sub-graph count)
        
        Returns:
            List of SubGraph objects
        """
        logger.info("🕸️  Generating evidence sub-graphs (cadavre exquis)...")
        logger.info(f"   Difficulty: {difficulty}/10")
        logger.info(f"   Target documents: {num_documents}")
        
        # Calculate number of sub-graphs based on difficulty and documents
        num_subgraphs = self._calculate_subgraph_count(difficulty, num_documents)
        
        # Distribution: 60% identity, 20% psychological, 20% crypto
        num_identity = int(num_subgraphs * 0.6)
        num_psychological = int(num_subgraphs * 0.2)
        num_crypto = int(num_subgraphs * 0.2)
        
        # Ensure at least 1 of each for higher difficulties
        if difficulty >= 5:
            num_identity = max(3, num_identity)
            num_psychological = max(2, num_psychological)
            num_crypto = max(2, num_crypto)
        
        # Add red herrings (20-30% of total)
        num_red_herrings = max(2, int(num_subgraphs * 0.25))
        
        logger.info(f"   Total sub-graphs: {num_subgraphs + num_red_herrings}")
        logger.info(f"      Identity chains: {num_identity} (60%)")
        logger.info(f"      Psychological chains: {num_psychological} (20%)")
        logger.info(f"      Cryptographic chains: {num_crypto} (20%)")
        logger.info(f"      Red herrings: {num_red_herrings} (25%)")
        logger.info("")
        
        subgraphs = []
        
        # Generate identity sub-graphs (contribute to WHO)
        for i in range(num_identity):
            sg = self._generate_identity_subgraph(
                f"identity_{i}",
                premise,
                political_context,
                difficulty
            )
            subgraphs.append(sg)
        
        # Generate psychological sub-graphs (contribute to WHY)
        for i in range(num_psychological):
            sg = self._generate_psychological_subgraph(
                f"psychological_{i}",
                premise,
                political_context,
                difficulty
            )
            subgraphs.append(sg)
        
        # Generate cryptographic sub-graphs (contribute to WHAT/HOW)
        # IMPORTANT: Guarantee at least one chain for WHAT and one for HOW
        crypto_assignments = [AnswerDimension.WHAT, AnswerDimension.HOW]
        
        for i in range(num_crypto):
            # First chain → WHAT, second chain → HOW, rest are random
            if i < len(crypto_assignments):
                contributes_to = crypto_assignments[i]
            else:
                contributes_to = random.choice([AnswerDimension.WHAT, AnswerDimension.HOW])
            
            sg = self._generate_crypto_subgraph(
                f"crypto_{i}",
                premise,
                political_context,
                difficulty,
                contributes_to
            )
            subgraphs.append(sg)
            logger.info(f"      crypto_{i} → {contributes_to.value.upper()}")
        
        # Generate red herring sub-graphs
        for i in range(num_red_herrings):
            sg = self._generate_red_herring_subgraph(
                f"red_herring_{i}",
                premise,
                political_context,
                difficulty
            )
            subgraphs.append(sg)
        
        logger.info(f"   ✅ Generated {len(subgraphs)} sub-graphs")
        logger.info("")
        
        return subgraphs
    
    def _calculate_subgraph_count(self, difficulty: int, num_documents: int) -> int:
        """Calculate how many sub-graphs to generate."""
        # Base: 1 sub-graph per 2-3 documents
        base_count = num_documents // 2
        
        # Adjust for difficulty
        if difficulty <= 3:
            return max(5, base_count - 2)
        elif difficulty <= 6:
            return max(8, base_count)
        else:
            return max(12, base_count + 2)
    
    def _generate_identity_subgraph(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        difficulty: int
    ) -> SubGraph:
        """Generate an identity chain sub-graph."""
        # Get architecture
        architecture = get_architecture_for_type("identity", difficulty)
        
        # Build sub-graph from architecture
        subgraph = SubGraph(
            subgraph_id=subgraph_id,
            subgraph_type=EvidenceType.IDENTITY,
            is_complete=True,
            is_red_herring=False,
            contributes_to=AnswerDimension.WHO,
            hop_count=len(architecture.nodes),
            difficulty=difficulty
        )
        
        # Create nodes based on architecture
        # This will be filled in by identity_nodes.py
        # For now, create placeholder structure
        subgraph.conclusion = f"Identity chain leading to conspirator from: {premise.who[:50]}"
        
        logger.info(f"      Created {subgraph_id}: {architecture.name} ({len(architecture.nodes)} nodes)")
        
        return subgraph
    
    def _generate_psychological_subgraph(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        difficulty: int
    ) -> SubGraph:
        """Generate a psychological pattern sub-graph."""
        architecture = get_architecture_for_type("psychological", difficulty)
        
        subgraph = SubGraph(
            subgraph_id=subgraph_id,
            subgraph_type=EvidenceType.PSYCHOLOGICAL,
            is_complete=True,
            is_red_herring=False,
            contributes_to=AnswerDimension.WHY,
            hop_count=len(architecture.nodes),
            difficulty=difficulty
        )
        
        subgraph.conclusion = f"Psychological pattern revealing motivation: {premise.why[:50]}"
        
        logger.info(f"      Created {subgraph_id}: {architecture.name} ({len(architecture.nodes)} nodes)")
        
        return subgraph
    
    def _generate_crypto_subgraph(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        difficulty: int,
        contributes_to: AnswerDimension
    ) -> SubGraph:
        """Generate a cryptographic sub-graph."""
        architecture = get_architecture_for_type("cryptographic", difficulty)
        
        subgraph = SubGraph(
            subgraph_id=subgraph_id,
            subgraph_type=EvidenceType.CRYPTOGRAPHIC,
            is_complete=True,
            is_red_herring=False,
            contributes_to=contributes_to,
            hop_count=len(architecture.nodes),
            difficulty=difficulty
        )
        
        if contributes_to == AnswerDimension.WHAT:
            subgraph.conclusion = f"Encrypted evidence revealing goal: {premise.what[:50]}"
        else:
            subgraph.conclusion = f"Encrypted evidence revealing method: {premise.how[:50]}"
        
        logger.info(f"      Created {subgraph_id}: {architecture.name} ({len(architecture.nodes)} nodes)")
        
        return subgraph
    
    def _generate_red_herring_subgraph(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        difficulty: int
    ) -> SubGraph:
        """Generate a broken/false evidence chain."""
        architecture = get_architecture_for_type("red_herring", difficulty)
        
        # Red herrings can be any type
        rh_type = random.choice([EvidenceType.IDENTITY, EvidenceType.PSYCHOLOGICAL])
        
        subgraph = SubGraph(
            subgraph_id=subgraph_id,
            subgraph_type=rh_type,
            is_complete=False,  # Broken chain
            is_red_herring=True,
            contributes_to=None,  # Doesn't contribute to answer
            hop_count=len(architecture.nodes),
            difficulty=difficulty
        )
        
        subgraph.conclusion = "Dead end - missing crucial connection"
        
        logger.info(f"      Created {subgraph_id}: RED HERRING ({len(architecture.nodes)} nodes)")
        
        return subgraph

