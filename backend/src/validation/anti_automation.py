"""
Anti-automation validation system.

This module validates that mysteries are:
1. TOO HARD for single LLM call (automation-resistant)
2. SOLVABLE with guided multi-hop reasoning (not impossible)
"""

import logging
from typing import List, Dict, Any
from ..models import Mystery, ValidationResult, ValidationStep, ProofTree
from ..utils import CerebrasClient


logger = logging.getLogger(__name__)


class AntiAutomationValidator:
    """Validate that mysteries require multi-hop reasoning."""
    
    def __init__(self, llm_client: CerebrasClient):
        self.llm = llm_client
    
    async def validate_mystery(self, mystery: Mystery) -> ValidationResult:
        """
        Complete validation: single-LLM test + multi-hop test.
        
        Args:
            mystery: Mystery to validate
        
        Returns:
            ValidationResult with pass/fail status
        """
        logger.info(f"🔍 Validating mystery: {mystery.metadata.mystery_id}")
        logger.info(f"   Question: {mystery.metadata.question}")
        logger.info(f"   Expected answer: {mystery.answer}")
        logger.info("")
        
        result = ValidationResult(mystery_id=mystery.metadata.mystery_id)
        
        # Test 1: Single LLM should FAIL
        logger.info("Test 1: Single-LLM attempt (should fail)...")
        single_llm_result = await self._test_single_llm(mystery)
        result.single_llm_response = single_llm_result["response"]
        result.single_llm_got_answer = single_llm_result["correct"]
        
        if single_llm_result["correct"]:
            logger.error("   ❌ Single LLM solved it! Mystery is too easy.")
            result.evaluate()
            return result
        else:
            logger.info("   ✅ Single LLM failed (good!)")
        
        logger.info("")
        
        # Test 2: Multi-hop should SUCCEED
        logger.info("Test 2: Multi-hop guided attempt (should succeed)...")
        multi_hop_result = await self._test_multi_hop(mystery)
        result.multi_hop_steps = multi_hop_result["steps"]
        result.multi_hop_reached_answer = multi_hop_result["reached_answer"]
        
        if not multi_hop_result["reached_answer"]:
            logger.error("   ❌ Multi-hop failed! Mystery is unsolvable.")
            result.evaluate()
            return result
        else:
            logger.info("   ✅ Multi-hop succeeded!")
        
        logger.info("")
        
        # Evaluate overall
        result.evaluate()
        
        if result.is_valid:
            logger.info("="*60)
            logger.info("✅ VALIDATION PASSED")
            logger.info("="*60)
            logger.info("Mystery is automation-resistant AND solvable!")
        else:
            logger.error("="*60)
            logger.error("❌ VALIDATION FAILED")
            logger.error("="*60)
            logger.error(f"Reason: {result.reason}")
        
        return result
    
    async def _test_single_llm(self, mystery: Mystery) -> Dict[str, Any]:
        """
        Test if single LLM can solve the mystery with all documents.
        Should FAIL for valid mysteries.
        """
        # Combine all documents into one prompt
        docs_text = "\n\n".join([
            f"DOCUMENT {i+1} ({doc['document_type']}):\n{self._format_document(doc)}"
            for i, doc in enumerate(mystery.documents)
        ])
        
        prompt = f"""You are a detective analyzing evidence. Answer the question based ONLY on the documents provided.

QUESTION: {mystery.metadata.question}

DOCUMENTS:
{docs_text}

Provide your answer in ONE WORD or SHORT PHRASE. Do not explain your reasoning.

ANSWER:"""
        
        try:
            response = await self.llm.generate(
                prompt,
                temperature=0.1,
                max_tokens=100
            )
            
            response = response.strip().lower()
            answer = mystery.answer.strip().lower()
            
            # Check if response contains the answer
            correct = (answer in response) or (response in answer)
            
            return {
                "response": response,
                "correct": correct
            }
        
        except Exception as e:
            logger.error(f"Single-LLM test error: {e}")
            return {
                "response": "",
                "correct": False
            }
    
    async def _test_multi_hop(self, mystery: Mystery) -> Dict[str, Any]:
        """
        Test if multi-hop guided reasoning can solve the mystery.
        Should SUCCEED for valid mysteries.
        """
        proof_tree = mystery.proof_tree
        validation_steps = proof_tree.get("validation_steps", [])
        
        steps_results = []
        accumulated_knowledge = []
        
        for step_data in validation_steps:
            step_num = step_data["step_number"]
            sub_question = step_data["sub_question"]
            required_docs = step_data["required_document_ids"]
            expected_inference = step_data["expected_inference"]
            
            logger.info(f"   Step {step_num}: {sub_question}")
            
            # Get required documents
            docs = [
                doc for doc in mystery.documents
                if doc["document_id"] in required_docs
            ]
            
            # Add accumulated knowledge
            docs_text = "\n\n".join([
                f"DOCUMENT ({doc['document_type']}):\n{self._format_document(doc)}"
                for doc in docs
            ])
            
            knowledge_text = ""
            if accumulated_knowledge:
                knowledge_text = "\n\nPREVIOUS FINDINGS:\n" + "\n".join(
                    f"- {k}" for k in accumulated_knowledge
                )
            
            prompt = f"""Analyze the documents and answer the question.

QUESTION: {sub_question}

DOCUMENTS:
{docs_text}
{knowledge_text}

Provide a concise answer based on the evidence.

ANSWER:"""
            
            try:
                response = await self.llm.generate(
                    prompt,
                    temperature=0.1,
                    max_tokens=200
                )
                
                response = response.strip()
                
                # Check if response matches expected inference (fuzzy match)
                matches = self._check_inference_match(response, expected_inference)
                
                step_result = ValidationStep(
                    step_number=step_num,
                    sub_question=sub_question,
                    llm_response=response,
                    expected_inference=expected_inference,
                    matches=matches,
                    confidence=0.8 if matches else 0.2
                )
                
                steps_results.append(step_result)
                
                if matches:
                    logger.info(f"      ✅ Correct: {response}")
                    accumulated_knowledge.append(response)
                else:
                    logger.error(f"      ❌ Wrong: {response}")
                    logger.error(f"      Expected: {expected_inference}")
                    # Don't accumulate wrong answers
                
            except Exception as e:
                logger.error(f"      ❌ Error: {e}")
                step_result = ValidationStep(
                    step_number=step_num,
                    sub_question=sub_question,
                    llm_response="",
                    expected_inference=expected_inference,
                    matches=False,
                    confidence=0.0
                )
                steps_results.append(step_result)
        
        # Check if final answer is reached
        all_passed = all(step.matches for step in steps_results)
        reached_answer = all_passed
        
        return {
            "steps": steps_results,
            "reached_answer": reached_answer
        }
    
    def _format_document(self, doc: Dict[str, Any]) -> str:
        """Format document for LLM prompt."""
        import json
        fields = doc.get("fields", {})
        return json.dumps(fields, indent=2)
    
    def _check_inference_match(self, response: str, expected: str) -> bool:
        """
        Check if LLM response matches expected inference.
        Uses fuzzy matching for flexibility.
        """
        response = response.lower().strip()
        expected = expected.lower().strip()
        
        # Exact match
        if response == expected:
            return True
        
        # Contains match
        if expected in response:
            return True
        
        # Reverse contains (for partial answers)
        if response in expected:
            return True
        
        # Token overlap (at least 50% of expected tokens in response)
        expected_tokens = set(expected.split())
        response_tokens = set(response.split())
        overlap = len(expected_tokens & response_tokens)
        
        if len(expected_tokens) > 0:
            similarity = overlap / len(expected_tokens)
            return similarity >= 0.5
        
        return False

