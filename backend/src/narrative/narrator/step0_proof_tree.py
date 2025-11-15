"""Step 0: Proof Tree Generation - create multi-hop reasoning structure."""

import logging
from typing import Dict, Any, List
from .identity_injector import IdentityInjector


logger = logging.getLogger(__name__)


PROOF_TREE_GENERATION_PROMPT = """You are designing a multi-hop reasoning puzzle for a detective mystery.

MYSTERY DETAILS:
Question: {question}
Answer: {answer}
Difficulty: {difficulty}/10

YOUR TASK:
Design a proof tree with {num_hops} inference nodes that connect evidence to the answer.

CRITICAL RULES FOR EVIDENCE NODES (no parents):

1. **USE INDIRECT IDENTIFIERS - NEVER THE ANSWER NAME!**
   - ❌ BAD: "John Smith accessed the building at 2:30 AM" (reveals answer!)
   - ✅ GOOD: "User ID 'jsmith' accessed the building at 2:30 AM" (obfuscated)
   - ✅ GOOD: "Badge #45123 scanned at entrance at 2:30 AM" (indirect)

2. **ONE IDENTIFIER PER NODE - KEEP THEM ATOMIC!**
   - ❌ BAD: "User 'jsmith' (Badge #123) accessed from IP 192.168.1.42"
   - ✅ GOOD: Create 3 SEPARATE nodes:
     * Node A: "IP 192.168.1.42 accessed server at 2:30 AM"
     * Node B: "User ID 'jsmith' logged in at 2:29 AM"
     * Node C: "Employee directory: User 'jsmith' has badge #123"

3. **SPLIT COMPLEX MAPPINGS INTO SEPARATE NODES!**
   - ❌ BAD: "HR links user 'jsmith' to employee #5873, device D-123, and badge #456"
   - ✅ GOOD: Create 3+ separate nodes:
     * "Device D-123 registered in IT asset database"
     * "Badge #456 issued to employee #5873"
     * "User ID 'jsmith' is employee #5873"

Use these identifier types:
- User IDs (jsmith, mpatel, etc.)
- Badge numbers (#12345)
- IP addresses (192.168.x.x)
- Device IDs (D-ABC123)
- Employee numbers (#5873)
- Session/Request IDs

RULES:
1. Start with direct observations from evidence (no parents) - USE INDIRECT IDs!
2. Build up to higher-level inferences (with parents)
3. Final nodes should lead to the answer
4. Each node requires 1-3 documents as evidence
5. More difficult = more hops and complex reasoning

INFERENCE NODE STRUCTURE:
- node_id: Unique ID like "node_1", "node_2", etc.
- inference: What is concluded at this step
- reasoning_type: Choose from:
  * "direct_observation" - Read directly from documents
  * "cross_reference" - Connect info across documents
  * "temporal_reasoning" - Timeline-based deduction
  * "contradiction_detection" - Find inconsistencies
  * "synthesis" - Combine multiple inferences
  * "deduction" - Logical reasoning from facts
- document_ids: List of document IDs needed (use generic like ["doc_1", "doc_2"])
- parent_nodes: List of node_ids that must be resolved first (empty for evidence-level nodes)

EXAMPLE STRUCTURE (5 hops - CORRECT WAY WITH ATOMIC NODES):
{{
  "answer": "John Smith",
  "inference_nodes": [
    {{
      "node_id": "node_1",
      "inference": "IP 192.168.1.42 accessed server files at 2:30 AM",
      "reasoning_type": "direct_observation",
      "document_ids": ["doc_server_log"],
      "parent_nodes": []
    }},
    {{
      "node_id": "node_2",
      "inference": "Badge #45123 scanned at server room door at 2:28 AM",
      "reasoning_type": "direct_observation",
      "document_ids": ["doc_badge_log"],
      "parent_nodes": []
    }},
    {{
      "node_id": "node_3",
      "inference": "User ID 'jsmith' logged in from IP 192.168.1.42 at 2:25 AM",
      "reasoning_type": "direct_observation",
      "document_ids": ["doc_network_log"],
      "parent_nodes": []
    }},
    {{
      "node_id": "node_4",
      "inference": "Employee #5873 has badge #45123",
      "reasoning_type": "direct_observation",
      "document_ids": ["doc_hr_badges"],
      "parent_nodes": []
    }},
    {{
      "node_id": "node_5",
      "inference": "Employee directory shows employee #5873 is John Smith with user ID 'jsmith'",
      "reasoning_type": "direct_observation",
      "document_ids": ["doc_hr_directory"],
      "parent_nodes": []
    }},
    {{
      "node_id": "node_6",
      "inference": "John Smith accessed the server room and files at 2:25-2:30 AM",
      "reasoning_type": "cross_reference",
      "document_ids": ["doc_server_log", "doc_badge_log", "doc_network_log", "doc_hr_badges", "doc_hr_directory"],
      "parent_nodes": ["node_1", "node_2", "node_3", "node_4", "node_5"]
    }}
  ]
}}

Now create a proof tree with {num_hops} inference nodes.

Output ONLY valid JSON:
{{
  "answer": "{answer}",
  "inference_nodes": [...]
}}"""


class ProofTreeGenerator:
    """Generate proof tree structure using LLM."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.identity_injector = IdentityInjector()
    
    async def generate_proof_tree(
        self,
        question: str,
        answer: str,
        difficulty: int,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a multi-hop proof tree for the mystery.
        
        Args:
            question: The mystery question
            answer: The answer to the mystery
            difficulty: Difficulty level (1-10)
            config: Configuration
        
        Returns:
            Proof tree dictionary
        """
        logger.info("🌳 Step 0: Generating proof tree...")
        logger.info(f"   Question: {question}")
        logger.info(f"   Answer: {answer}")
        logger.info(f"   Difficulty: {difficulty}/10")
        
        # Determine number of hops based on difficulty
        num_hops = self._calculate_hops(difficulty)
        logger.info(f"   Target hops: {num_hops}")
        
        # Build prompt
        prompt = PROOF_TREE_GENERATION_PROMPT.format(
            question=question,
            answer=answer,
            difficulty=difficulty,
            num_hops=num_hops
        )
        
        # Generate with LLM
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 8000)  # Increased for more hops!
            )
            
            # Validate structure
            proof_tree = self._validate_and_enhance(response, question, answer, num_hops)
            
            # CRITICAL: Inject missing identity nodes programmatically!
            proof_tree = self.identity_injector.inject_identity_nodes(proof_tree, answer)
            
            # Rebuild validation steps after injection
            proof_tree["validation_steps"] = self._build_validation_steps(proof_tree["inference_nodes"])
            
            logger.info(f"   ✅ Generated {len(proof_tree['inference_nodes'])} inference nodes")
            
            # Log structure
            for node in proof_tree['inference_nodes']:
                parents_str = f" (parents: {node['parent_nodes']})" if node['parent_nodes'] else " (evidence)"
                logger.info(f"      - {node['node_id']}: {node['reasoning_type']}{parents_str}")
            
            return proof_tree
        
        except Exception as e:
            logger.error(f"   ❌ Proof tree generation failed: {e}")
            # Fallback to simple proof tree
            fallback = self._create_fallback_proof_tree(question, answer, num_hops)
            # Still apply identity injection even to fallback!
            fallback = self.identity_injector.inject_identity_nodes(fallback, answer)
            fallback["validation_steps"] = self._build_validation_steps(fallback["inference_nodes"])
            return fallback
    
    def _calculate_hops(self, difficulty: int) -> int:
        """
        Calculate number of hops based on difficulty.
        
        Since we now require ATOMIC clues (one identifier per node),
        we need MORE nodes to complete the reasoning chain!
        """
        # With atomic clues, we need more nodes for same difficulty
        # Difficulty 1-3: 5-6 evidence nodes
        # Difficulty 4-6: 7-9 evidence nodes
        # Difficulty 7-8: 10-12 evidence nodes
        # Difficulty 9-10: 13-15 evidence nodes
        
        if difficulty <= 3:
            return 5 + difficulty  # 6-8 total
        elif difficulty <= 6:
            return 7 + (difficulty - 3)  # 8-11 total
        elif difficulty <= 8:
            return 11 + (difficulty - 6)  # 12-14 total
        else:
            return 14 + (difficulty - 8)  # 15-17 total
    
    def _validate_and_enhance(
        self,
        proof_tree: Dict[str, Any],
        question: str,
        answer: str,
        expected_hops: int
    ) -> Dict[str, Any]:
        """Validate and enhance the generated proof tree."""
        
        # Ensure required fields
        if "answer" not in proof_tree:
            proof_tree["answer"] = answer
        
        if "inference_nodes" not in proof_tree:
            raise ValueError("No inference_nodes in proof tree")
        
        nodes = proof_tree["inference_nodes"]
        
        # Add missing fields
        for i, node in enumerate(nodes):
            if "node_id" not in node:
                node["node_id"] = f"node_{i+1}"
            
            if "parent_nodes" not in node:
                node["parent_nodes"] = []
            
            if "document_ids" not in node:
                node["document_ids"] = [f"doc_{i+1}"]
            
            if "reasoning_type" not in node:
                node["reasoning_type"] = "direct_observation" if not node["parent_nodes"] else "synthesis"
        
        # Add total_hops
        proof_tree["total_hops"] = len(nodes)
        
        # Build validation steps (for anti-automation validator)
        proof_tree["validation_steps"] = self._build_validation_steps(nodes)
        
        return proof_tree
    
    def _build_validation_steps(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build validation steps from inference nodes."""
        validation_steps = []
        
        for i, node in enumerate(nodes):
            # Create sub-question based on reasoning type
            sub_question = self._generate_sub_question(node)
            
            step = {
                "step_number": i + 1,
                "sub_question": sub_question,
                "required_document_ids": node["document_ids"],
                "expected_inference": node["inference"],
                "inference_node_id": node["node_id"]
            }
            
            validation_steps.append(step)
        
        return validation_steps
    
    def _generate_sub_question(self, node: Dict[str, Any]) -> str:
        """Generate a sub-question for validation."""
        reasoning_type = node.get("reasoning_type", "direct_observation")
        inference = node.get("inference", "")
        
        templates = {
            "direct_observation": "What specific information can you find in the documents?",
            "cross_reference": "What connections exist between these documents?",
            "temporal_reasoning": "What timeline can you establish?",
            "contradiction_detection": "What inconsistencies do you notice?",
            "synthesis": "What conclusion can you draw from combining this information?",
            "deduction": "What can you logically deduce?"
        }
        
        question = templates.get(reasoning_type, "What can you infer?")
        return f"{question} (Looking for: {inference})"
    
    def _create_fallback_proof_tree(
        self,
        question: str,
        answer: str,
        num_hops: int
    ) -> Dict[str, Any]:
        """Create a simple fallback proof tree if LLM generation fails."""
        logger.warning("   ⚠️  Using fallback proof tree")
        
        nodes = []
        
        # Create simple linear chain
        for i in range(num_hops):
            node = {
                "node_id": f"node_{i+1}",
                "inference": f"Inference step {i+1} leading to {answer}",
                "reasoning_type": "direct_observation" if i < 2 else "synthesis",
                "document_ids": [f"doc_{i+1}", f"doc_{i+2}"],
                "parent_nodes": [f"node_{i}"] if i > 0 else []
            }
            nodes.append(node)
        
        proof_tree = {
            "answer": answer,
            "inference_nodes": nodes,
            "total_hops": num_hops,
            "validation_steps": self._build_validation_steps(nodes)
        }
        
        return proof_tree

