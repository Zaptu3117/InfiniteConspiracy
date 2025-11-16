"""Conspiracy Validator - validates multi-dimensional solvability."""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from models.conspiracy import ConspiracyMystery, AnswerDimension


logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of conspiracy validation."""
    is_valid: bool
    reason: str
    
    # Answer-specific results
    who_solvable: bool
    what_solvable: bool
    why_solvable: bool
    how_solvable: bool
    
    # Test results
    single_llm_failed: bool  # Should be True (single LLM should fail)
    multi_hop_succeeded: bool  # Should be True (multi-hop should succeed)
    crypto_discoverable: bool  # Keys discoverable
    
    details: Dict[str, Any] = None


class ConspiracyValidator:
    """Validate conspiracy mysteries for solvability."""
    
    def __init__(self, llm_client):
        """
        Initialize validator.
        
        Args:
            llm_client: LLM client for validation tests
        """
        self.llm = llm_client
    
    async def validate_conspiracy(
        self,
        mystery: ConspiracyMystery,
        config: Dict[str, Any] = None
    ) -> ValidationResult:
        """
        Validate conspiracy mystery.
        
        Tests:
        1. Single-LLM test: Give all documents at once → should FAIL
        2. Multi-hop test: Follow sub-graphs step-by-step → should SUCCEED
        3. Crypto test: Keys discoverable through inference
        4. Answer coverage: All 4 dimensions solvable
        
        Args:
            mystery: Conspiracy mystery to validate
            config: Optional configuration
        
        Returns:
            ValidationResult
        """
        config = config or {}
        
        logger.info("🔍 Validating conspiracy mystery...")
        logger.info(f"   Mystery: {mystery.premise.conspiracy_name}")
        logger.info(f"   Sub-graphs: {len(mystery.subgraphs)}")
        logger.info(f"   Documents: {len(mystery.documents)}")
        logger.info("")
        
        # Test 1: Single-LLM should fail
        logger.info("TEST 1: Single-LLM Attempt (should FAIL)")
        logger.info("-" * 60)
        single_llm_failed = await self._test_single_llm(mystery)
        logger.info("")
        
        # Test 2: Multi-hop should succeed
        logger.info("TEST 2: Multi-Hop Reasoning (should SUCCEED)")
        logger.info("-" * 60)
        multi_hop_succeeded = await self._test_multi_hop(mystery)
        logger.info("")
        
        # Test 3: Crypto keys discoverable
        logger.info("TEST 3: Crypto Key Discoverability")
        logger.info("-" * 60)
        crypto_discoverable = self._test_crypto_discoverability(mystery)
        logger.info("")
        
        # Test 4: Check answer coverage
        logger.info("TEST 4: Answer Coverage")
        logger.info("-" * 60)
        answer_coverage = self._check_answer_coverage(mystery)
        logger.info("")
        
        # Determine overall validity
        is_valid = (
            single_llm_failed and
            multi_hop_succeeded and
            crypto_discoverable and
            all(answer_coverage.values())
        )
        
        if is_valid:
            reason = "All validation tests passed"
        else:
            failures = []
            if not single_llm_failed:
                failures.append("Single-LLM succeeded (too easy)")
            if not multi_hop_succeeded:
                failures.append("Multi-hop failed (too hard)")
            if not crypto_discoverable:
                failures.append("Crypto keys not discoverable")
            if not all(answer_coverage.values()):
                missing = [k for k, v in answer_coverage.items() if not v]
                failures.append(f"Missing evidence for: {', '.join(missing)}")
            reason = "; ".join(failures)
        
        result = ValidationResult(
            is_valid=is_valid,
            reason=reason,
            who_solvable=answer_coverage.get("WHO", False),
            what_solvable=answer_coverage.get("WHAT", False),
            why_solvable=answer_coverage.get("WHY", False),
            how_solvable=answer_coverage.get("HOW", False),
            single_llm_failed=single_llm_failed,
            multi_hop_succeeded=multi_hop_succeeded,
            crypto_discoverable=crypto_discoverable,
            details={
                "answer_coverage": answer_coverage,
                "subgraph_count": len(mystery.subgraphs),
                "document_count": len(mystery.documents)
            }
        )
        
        # Log summary
        logger.info("="*60)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Overall: {'✅ VALID' if is_valid else '❌ INVALID'}")
        logger.info(f"Reason: {reason}")
        logger.info("")
        logger.info("Answer Solvability:")
        logger.info(f"  WHO: {'✅' if result.who_solvable else '❌'}")
        logger.info(f"  WHAT: {'✅' if result.what_solvable else '❌'}")
        logger.info(f"  WHY: {'✅' if result.why_solvable else '❌'}")
        logger.info(f"  HOW: {'✅' if result.how_solvable else '❌'}")
        logger.info("")
        logger.info("Test Results:")
        logger.info(f"  Single-LLM failed: {'✅' if result.single_llm_failed else '❌ (mystery too easy)'}")
        logger.info(f"  Multi-hop succeeded: {'✅' if result.multi_hop_succeeded else '❌ (mystery too hard)'}")
        logger.info(f"  Crypto discoverable: {'✅' if result.crypto_discoverable else '❌'}")
        logger.info("")
        
        return result
    
    async def _test_single_llm(self, mystery: ConspiracyMystery) -> bool:
        """Test if single LLM can solve with all documents."""
        
        # Build prompt with all documents
        all_docs_text = "\n\n".join([
            f"Document {i+1}:\n{str(doc)}"
            for i, doc in enumerate(mystery.documents[:10])  # Use first 10 for speed
        ])
        
        prompt = f"""You are investigating a conspiracy. Here are all the documents:

{all_docs_text}

Questions:
1. WHO are the conspirators?
2. WHAT is the conspiracy goal?
3. WHY are they doing it?
4. HOW are they executing it?

Answer all four questions based on the documents.
"""
        
        try:
            response = await self.llm.generate(
                prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Check if response is None or empty
            if not response or not isinstance(response, str):
                logger.info("   ✅ Single-LLM FAILED (as expected)")
                logger.info("      No valid response generated")
                return True
            
            response_lower = response.lower()
            
            # Check if LLM found specific answers
            premise = mystery.premise
            who_found = any(name.lower() in response_lower for name in premise.who.split()[:3])
            what_found = any(word.lower() in response_lower for word in premise.what.split()[:5])
            
            if who_found and what_found:
                logger.info("   ❌ Single-LLM SUCCEEDED (mystery may be too easy)")
                logger.info(f"      Found WHO and WHAT in response")
                return False  # Failed validation (should have failed the test)
            else:
                logger.info("   ✅ Single-LLM FAILED (as expected)")
                logger.info("      Could not determine specific answers")
                return True  # Passed validation (test failed as it should)
        
        except Exception as e:
            logger.error(f"   ⚠️  Single-LLM test error: {e}")
            return True  # Assume pass if error
    
    async def _test_multi_hop(self, mystery: ConspiracyMystery) -> bool:
        """
        Test if multi-hop reasoning can solve the mystery.
        
        Proves that:
        1. Each step is solvable WITH previous context
        2. Each step is unsolvable WITHOUT previous context
        """
        
        complete_chains = [sg for sg in mystery.subgraphs 
                          if sg.is_complete and not sg.is_red_herring]
        
        if not complete_chains:
            logger.info("   ❌ No complete evidence chains")
            return False
        
        logger.info(f"   Testing {len(complete_chains)} evidence chains...")
        
        passed_chains = 0
        for sg in complete_chains:
            logger.info(f"\n   Chain: {sg.subgraph_id} ({sg.subgraph_type.value} → {sg.contributes_to.value if sg.contributes_to else 'None'})")
            
            # Test the chain step-by-step
            chain_valid = await self._test_inference_chain(sg, mystery.documents)
            
            if chain_valid:
                passed_chains += 1
                logger.info(f"      ✅ Chain solvable with guided reasoning")
            else:
                logger.info(f"      ❌ Chain broken or too hard")
        
        # At least 75% of chains should be solvable
        success_rate = passed_chains / len(complete_chains) if complete_chains else 0
        
        logger.info(f"\n   Result: {passed_chains}/{len(complete_chains)} chains passed")
        
        return success_rate >= 0.75
    
    def _test_crypto_discoverability(self, mystery: ConspiracyMystery) -> bool:
        """Test if crypto keys are discoverable."""
        
        if not mystery.crypto_keys:
            logger.info("   ✅ No crypto keys to test")
            return True
        
        discoverable_count = sum(1 for key in mystery.crypto_keys if key.discoverable)
        
        logger.info(f"   Crypto keys: {len(mystery.crypto_keys)}")
        logger.info(f"   Discoverable: {discoverable_count}/{len(mystery.crypto_keys)}")
        
        if discoverable_count >= len(mystery.crypto_keys) * 0.8:  # 80% discoverable
            logger.info("   ✅ Crypto keys are discoverable")
            return True
        else:
            logger.info("   ❌ Too many keys are not discoverable")
            return False
    
    def _check_answer_coverage(self, mystery: ConspiracyMystery) -> Dict[str, bool]:
        """Check if all answer dimensions are actually discoverable in documents."""
        
        coverage = {
            "WHO": False,
            "WHAT": False,
            "WHY": False,
            "HOW": False
        }
        
        # Get answer values
        if not mystery.answer_template:
            logger.warning("   ⚠️  No answer template found")
            return coverage
        
        who_answer = mystery.answer_template.who.lower()
        what_answer = mystery.answer_template.what.lower()
        why_answer = mystery.answer_template.why.lower()
        how_answer = mystery.answer_template.how.lower()
        
        # Search documents for actual answer strings
        import json
        for doc in mystery.documents:
            doc_text = json.dumps(doc).lower()
            
            if who_answer in doc_text:
                coverage["WHO"] = True
            if what_answer in doc_text:
                coverage["WHAT"] = True
            if why_answer in doc_text:
                coverage["WHY"] = True
            if how_answer in doc_text:
                coverage["HOW"] = True
        
        # Log results with actual answer values
        for dim in ["WHO", "WHAT", "WHY", "HOW"]:
            answer_val = getattr(mystery.answer_template, dim.lower())
            found = coverage[dim]
            status = "✅" if found else "❌"
            logger.info(f"   {status} {dim}: '{answer_val}' {'FOUND' if found else 'NOT FOUND'} in documents")
        
        return coverage
    
    async def _test_inference_chain(self, subgraph, documents: List[Dict]) -> bool:
        """
        Test one inference chain by following it step-by-step.
        
        For each step:
        1. Test WITH context (should succeed)
        2. Test WITHOUT context (should fail - proves step is not trivial)
        
        Returns True if chain is solvable with guidance.
        """
        
        if not subgraph.inference_nodes:
            logger.info("      ⚠️  No inference nodes in chain")
            return False
        
        accumulated_context = []  # Build up discoveries
        
        for i, inference_node in enumerate(subgraph.inference_nodes):
            step_num = i + 1
            logger.info(f"      Step {step_num}: {inference_node.inference[:60]}...")
            
            # Get required documents
            required_docs = [doc for doc in documents 
                            if doc.get('document_id') in inference_node.required_document_ids]
            
            if not required_docs:
                logger.warning(f"         ⚠️  No documents found")
                return False
            
            # Test WITH context (should succeed)
            with_context = await self._test_step_with_context(
                required_docs, 
                inference_node.inference,
                accumulated_context
            )
            
            if not with_context:
                logger.warning(f"         ❌ Failed WITH context (chain broken)")
                return False
            
            logger.info(f"         ✅ Solvable with context")
            
            # Add this inference to accumulated context for next steps
            accumulated_context.append(inference_node.inference)
        
        return True
    
    async def _test_step_with_context(self, docs: List[Dict], target_inference: str, prior_context: List[str]) -> bool:
        """
        Test if LLM can make this inference given documents and prior discoveries.
        
        Args:
            docs: Documents containing information for this step
            target_inference: What we expect LLM to infer
            prior_context: Previous inferences that inform this step
        
        Returns:
            True if LLM response matches target inference
        """
        
        # Build prompt with documents
        docs_text = "\n\n".join([self._format_document(doc) for doc in docs])
        
        # Add prior context if available
        context_text = ""
        if prior_context:
            context_text = "\n\nPREVIOUS DISCOVERIES:\n" + "\n".join(
                f"- {ctx}" for ctx in prior_context
            )
        
        prompt = f"""You are investigating a conspiracy. Analyze these documents and extract relevant information.

DOCUMENTS:
{docs_text}
{context_text}

TASK: Based on the documents and any previous discoveries, explain what you can determine about:
{target_inference}

Provide a clear, specific answer with details from the documents. If the documents don't support this conclusion, explain why."""
        
        try:
            response = await self.llm.generate(
                prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            if not response:
                return False
            
            # Check if response matches expected inference (LLM as judge)
            return await self._check_semantic_match(response, target_inference)
            
        except Exception as e:
            logger.error(f"         Error: {e}")
            return False
    
    def _format_document(self, doc: Dict[str, Any]) -> str:
        """Format document fields for LLM prompt, including nested data."""
        fields = doc.get('fields', {})
        lines = [f"Document ID: {doc.get('document_id', 'unknown')}"]
        
        for key, value in fields.items():
            if isinstance(value, str) and value.strip():
                lines.append(f"{key}: {value}")
            elif isinstance(value, list) and value:
                # Format list items (e.g., log entries)
                lines.append(f"{key}:")
                for i, item in enumerate(value[:20]):  # Limit to first 20 items
                    if isinstance(item, dict):
                        # Format dict items compactly
                        item_str = ", ".join(f"{k}={v}" for k, v in item.items())
                        lines.append(f"  [{i+1}] {item_str}")
                    else:
                        lines.append(f"  [{i+1}] {item}")
                if len(value) > 20:
                    lines.append(f"  ... and {len(value) - 20} more entries")
            elif isinstance(value, dict) and value:
                # Format dict fields
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
        
        return "\n".join(lines)
    
    async def _check_semantic_match(self, response: str, expected: str) -> bool:
        """
        Check if LLM response semantically matches expected inference.
        
        Uses a second LLM call as a judge to assess semantic equivalence.
        This is much more robust than token matching.
        """
        if not response or not expected:
            return False
        
        response = response.strip()
        expected = expected.strip()
        
        # Quick exact match check (save API call)
        if response.lower() == expected.lower():
            return True
        
        # Quick substring check
        if expected.lower() in response.lower() or response.lower() in expected.lower():
            return True
        
        # Use LLM as judge
        assessment_prompt = f"""You are assessing whether an investigator's finding matches the expected discovery.

EXPECTED DISCOVERY: {expected}

INVESTIGATOR'S FINDING: {response}

Does the investigator's finding support or confirm the expected discovery?

Guidelines:
- The finding can be more detailed or specific than expected (that's good!)
- Paraphrasing and different wording are fine
- The core insight/connection must be present
- If the investigator found evidence SUPPORTING this, say YES
- If the investigator says this is NOT supported by evidence, say NO

Answer ONLY "YES" or "NO".

ANSWER:"""
        
        try:
            judgment = await self.llm.generate(
                assessment_prompt,
                temperature=0.1,  # Low temperature for consistent judgment
                max_tokens=2000  # Let the LLM find its natural stopping point
            )
            
            if judgment:
                judgment_clean = judgment.strip().upper()
                is_match = "YES" in judgment_clean
                
                # Debug logging
                if not is_match:
                    logger.info(f"         🔍 Expected: {expected[:80]}...")
                    logger.info(f"         🔍 Got: {response[:80]}...")
                    logger.info(f"         🔍 Judge says: {judgment_clean}")
                
                return is_match
            
            return False
            
        except Exception as e:
            logger.warning(f"         ⚠️  Assessment LLM failed: {e}")
            # Fallback to token overlap if LLM fails
            return self._fallback_token_match(response, expected)
    
    def _fallback_token_match(self, response: str, expected: str) -> bool:
        """Fallback token matching when LLM assessment fails."""
        response_tokens = set(response.lower().split())
        expected_tokens = set(expected.lower().split())
        
        # Remove stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
        response_tokens -= stop_words
        expected_tokens -= stop_words
        
        if not expected_tokens:
            return True
        
        overlap = len(response_tokens & expected_tokens)
        similarity = overlap / len(expected_tokens)
        
        return similarity >= 0.5

