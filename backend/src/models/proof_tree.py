"""Proof tree data models for multi-hop reasoning validation."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class InferenceNode(BaseModel):
    """A single inference in the reasoning chain."""
    
    node_id: str
    inference: str  # The conclusion drawn at this step
    document_ids: List[str]  # Documents required for this inference
    reasoning_type: str  # Type of reasoning (direct_observation, cross_reference, etc.)
    confidence_required: float = 0.8
    parent_nodes: List[str] = Field(default_factory=list)
    children_nodes: List[str] = Field(default_factory=list)


class ProofStep(BaseModel):
    """A step in the proof validation process."""
    
    step_number: int
    sub_question: str  # Question to ask LLM for this step
    required_document_ids: List[str]  # Documents needed for this step
    expected_inference: str  # What the LLM should deduce
    inference_node_id: str  # Reference to the inference node
    prerequisites: List[int] = Field(default_factory=list)  # Previous step numbers required


class ProofTree(BaseModel):
    """
    Complete proof tree structure for a mystery.
    This validates that the mystery requires multi-hop reasoning.
    """
    
    # The final answer
    answer: str
    
    # All inference nodes (graph structure)
    inference_nodes: List[InferenceNode] = Field(default_factory=list)
    
    # Ordered steps for validation
    validation_steps: List[ProofStep] = Field(default_factory=list)
    
    # Evidence layer (documents)
    evidence_document_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    min_hops: int = 3
    max_hops: int = 7
    total_hops: int = 0
    
    def build_validation_steps(self):
        """Build ordered validation steps from inference nodes."""
        # Topological sort of inference nodes
        sorted_nodes = self._topological_sort()
        
        self.validation_steps = []
        for i, node in enumerate(sorted_nodes):
            step = ProofStep(
                step_number=i + 1,
                sub_question=self._generate_sub_question(node),
                required_document_ids=node.document_ids,
                expected_inference=node.inference,
                inference_node_id=node.node_id,
                prerequisites=self._get_prerequisites(node, sorted_nodes)
            )
            self.validation_steps.append(step)
        
        self.total_hops = len(self.validation_steps)
    
    def _topological_sort(self) -> List[InferenceNode]:
        """Sort nodes in dependency order (bottom-up from evidence)."""
        # Find nodes with no parents (evidence-level inferences)
        no_parents = [n for n in self.inference_nodes if not n.parent_nodes]
        
        sorted_nodes = []
        visited = set()
        
        def visit(node: InferenceNode):
            if node.node_id in visited:
                return
            visited.add(node.node_id)
            
            # Visit parents first
            for parent_id in node.parent_nodes:
                parent = next((n for n in self.inference_nodes if n.node_id == parent_id), None)
                if parent:
                    visit(parent)
            
            sorted_nodes.append(node)
        
        for node in no_parents:
            visit(node)
        
        # Visit any remaining nodes
        for node in self.inference_nodes:
            visit(node)
        
        return sorted_nodes
    
    def _generate_sub_question(self, node: InferenceNode) -> str:
        """Generate a question for this inference node."""
        reasoning_prompts = {
            "direct_observation": "What information can you directly extract from these documents?",
            "cross_reference": "What connections can you find between these documents?",
            "temporal_reasoning": "What timeline can you establish from these documents?",
            "contradiction_detection": "What contradictions or inconsistencies do you find?",
            "synthesis": "What conclusion can you draw by combining this information?",
            "deduction": "Based on the information, what can you deduce?"
        }
        
        prompt = reasoning_prompts.get(node.reasoning_type, "What can you infer from these documents?")
        return f"{prompt} Expected: {node.inference}"
    
    def _get_prerequisites(self, node: InferenceNode, sorted_nodes: List[InferenceNode]) -> List[int]:
        """Get step numbers of prerequisite nodes."""
        prereqs = []
        for parent_id in node.parent_nodes:
            for i, sorted_node in enumerate(sorted_nodes):
                if sorted_node.node_id == parent_id:
                    prereqs.append(i + 1)
        return prereqs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "answer": self.answer,
            "inference_nodes": [node.dict() for node in self.inference_nodes],
            "validation_steps": [step.dict() for step in self.validation_steps],
            "evidence_document_ids": self.evidence_document_ids,
            "total_hops": self.total_hops,
            "min_hops": self.min_hops,
            "max_hops": self.max_hops
        }

