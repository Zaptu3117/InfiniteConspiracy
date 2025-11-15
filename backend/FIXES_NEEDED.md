# Required Code Fixes

This document provides specific code changes needed to fix the identified issues.

---

## 🔴 CRITICAL FIX #1: Multi-Hop Validation

**File:** `backend/src/validation/conspiracy_validator.py`  
**Lines:** 213-242  
**Function:** `_test_multi_hop()`

### Current Code (BROKEN):
```python
async def _test_multi_hop(self, mystery: ConspiracyMystery) -> bool:
    """Test if multi-hop reasoning can solve."""
    
    # Simplified: Check if there are complete chains to answers
    # In full implementation, would follow each sub-graph step-by-step
    
    complete_chains = [sg for sg in mystery.subgraphs if sg.is_complete and not sg.is_red_herring]
    
    if not complete_chains:
        logger.info("   ❌ No complete evidence chains")
        return False
    
    # ... just checks structure, doesn't test with LLM
    return True
```

### Fixed Code:
```python
async def _test_multi_hop(self, mystery: ConspiracyMystery) -> bool:
    """Test if multi-hop reasoning can solve."""
    
    complete_chains = [sg for sg in mystery.subgraphs if sg.is_complete and not sg.is_red_herring]
    
    if not complete_chains:
        logger.info("   ❌ No complete evidence chains")
        return False
    
    # ACTUAL TEST: Verify each inference step with LLM
    logger.info(f"   Testing {len(complete_chains)} evidence chains...")
    
    passed_chains = 0
    for sg in complete_chains:
        chain_valid = await self._test_inference_chain(sg, mystery.documents)
        if chain_valid:
            passed_chains += 1
    
    # At least 75% of chains should be solvable
    success_rate = passed_chains / len(complete_chains)
    
    if success_rate >= 0.75:
        logger.info(f"   ✅ Multi-hop CAN succeed ({passed_chains}/{len(complete_chains)} chains)")
        return True
    else:
        logger.info(f"   ❌ Multi-hop FAILED ({passed_chains}/{len(complete_chains)} chains)")
        return False

async def _test_inference_chain(self, subgraph: SubGraph, documents: List[Dict]) -> bool:
    """Test if a single inference chain is solvable with LLM."""
    
    # For each inference node in the chain
    for inference_node in subgraph.inference_nodes:
        # Get required documents
        required_docs = [
            doc for doc in documents 
            if doc.get('document_id') in inference_node.required_document_ids
        ]
        
        if not required_docs:
            logger.warning(f"      ⚠️  Inference {inference_node.node_id}: No documents found")
            return False
        
        # Build test prompt
        docs_text = "\n\n".join([
            f"Document {doc.get('document_id')}:\n{self._format_document(doc)}"
            for doc in required_docs
        ])
        
        prompt = f"""Analyze these documents and answer the question.

{docs_text}

Question: {inference_node.inference}

Provide a concise answer based ONLY on the documents."""
        
        try:
            response = await self.llm.generate(
                prompt,
                temperature=0.3,
                max_tokens=300
            )
            
            if not response:
                logger.warning(f"      ⚠️  Inference {inference_node.node_id}: No LLM response")
                return False
            
            # Check if response matches expected inference (fuzzy)
            response_lower = response.lower()
            expected_lower = inference_node.inference.lower()
            
            # Check for semantic overlap
            response_words = set(response_lower.split())
            expected_words = set(expected_lower.split())
            overlap = len(response_words & expected_words)
            similarity = overlap / max(len(expected_words), 1)
            
            if similarity < 0.5:
                logger.warning(f"      ⚠️  Inference {inference_node.node_id}: Low similarity ({similarity:.2f})")
                return False
            
        except Exception as e:
            logger.error(f"      ❌ Inference {inference_node.node_id}: Error - {e}")
            return False
    
    return True

def _format_document(self, doc: Dict[str, Any]) -> str:
    """Format document for LLM prompt."""
    fields = doc.get('fields', {})
    lines = []
    for key, value in fields.items():
        if isinstance(value, str):
            lines.append(f"{key}: {value}")
    return "\n".join(lines)
```

---

## 🔴 CRITICAL FIX #2: Empty Response Handling

**File:** `backend/src/validation/anti_automation.py`  
**Lines:** 188-191

### Current Code (BROKEN):
```python
# Check if response is None or empty
if not response or not isinstance(response, str):
    logger.info("   ✅ Single-LLM FAILED (as expected)")
    logger.info("      No valid response generated")
    return True  # WRONG!
```

### Fixed Code:
```python
# Check if response is None or empty
if not response or not isinstance(response, str):
    logger.error("   ❌ Single-LLM test INVALID - no response from LLM")
    logger.error("      This is a test failure, not a validation pass")
    raise ValueError(
        "Single-LLM test failed: LLM did not generate a response. "
        "This could be due to API errors, rate limits, or connectivity issues. "
        "Retry the validation."
    )
```

---

## 🔴 CRITICAL FIX #3: Arkiv Import Issue

**Action:** Delete redundant directory

```bash
rm -rf backend/src/arkiv/
```

**File:** `backend/test_setup.py`  
**Line:** 45

### Current Code (BROKEN):
```python
try:
    from arkiv import ArkivClient, EntityBuilder, ArkivPusher
    tests.append(("arkiv", True, ""))
except Exception as e:
    tests.append(("arkiv", False, str(e)))
```

### Fixed Code:
```python
try:
    from arkiv_integration import ArkivClient, EntityBuilder, ArkivPusher
    tests.append(("arkiv_integration", True, ""))
except Exception as e:
    tests.append(("arkiv_integration", False, str(e)))
```

---

## 🔴 CRITICAL FIX #4: Crypto Key Validation

**File:** `backend/src/validation/conspiracy_validator.py`  
**Lines:** 244-261

### Current Code (BROKEN):
```python
def _test_crypto_discoverability(self, mystery: ConspiracyMystery) -> bool:
    """Test if crypto keys are discoverable."""
    
    if not mystery.crypto_keys:
        logger.info("   ✅ No crypto keys to test")
        return True
    
    discoverable_count = sum(1 for key in mystery.crypto_keys if key.discoverable)
    
    if discoverable_count >= len(mystery.crypto_keys) * 0.8:  # 80% discoverable
        logger.info("   ✅ Crypto keys are discoverable")
        return True
```

### Fixed Code:
```python
async def _test_crypto_discoverability(self, mystery: ConspiracyMystery) -> bool:
    """Test if crypto keys are ACTUALLY discoverable via inference."""
    
    if not mystery.crypto_keys:
        logger.info("   ✅ No crypto keys to test")
        return True
    
    logger.info(f"   Testing {len(mystery.crypto_keys)} crypto keys...")
    
    discoverable_count = 0
    
    for crypto_key in mystery.crypto_keys:
        # Find documents containing hints
        hint_docs = [
            doc for doc in mystery.documents
            if doc.get('document_id') in crypto_key.hint_documents
        ]
        
        if not hint_docs:
            logger.warning(f"      ⚠️  Key {crypto_key.key_id}: No hint documents")
            continue
        
        # Test if LLM can infer the key from hints
        can_infer = await self._test_key_inference(crypto_key, hint_docs)
        
        if can_infer:
            discoverable_count += 1
            logger.info(f"      ✅ Key {crypto_key.key_id}: Discoverable")
        else:
            logger.warning(f"      ❌ Key {crypto_key.key_id}: NOT discoverable")
    
    success_rate = discoverable_count / len(mystery.crypto_keys)
    
    if success_rate >= 0.8:
        logger.info(f"   ✅ Crypto keys are discoverable ({discoverable_count}/{len(mystery.crypto_keys)})")
        return True
    else:
        logger.info(f"   ❌ Too many keys not discoverable ({discoverable_count}/{len(mystery.crypto_keys)})")
        return False

async def _test_key_inference(self, crypto_key, hint_docs) -> bool:
    """Test if LLM can infer the key from hint documents."""
    
    docs_text = "\n\n".join([
        f"Document:\n{self._format_document(doc)}"
        for doc in hint_docs
    ])
    
    prompt = f"""Based on these documents, what is the key or password?

{docs_text}

Hint: {crypto_key.inference_description}

What is the key?"""
    
    try:
        response = await self.llm.generate(
            prompt,
            temperature=0.3,
            max_tokens=200
        )
        
        if not response:
            return False
        
        # Check if response contains the key
        response_lower = response.lower().strip()
        key_lower = crypto_key.key_value.lower().strip()
        
        # Exact match or key appears in response
        if key_lower in response_lower or response_lower in key_lower:
            return True
        
        # Check token overlap
        response_tokens = set(response_lower.split())
        key_tokens = set(key_lower.split())
        overlap = len(response_tokens & key_tokens)
        
        return overlap >= len(key_tokens) * 0.7  # 70% overlap
        
    except Exception as e:
        logger.error(f"      Error testing key inference: {e}")
        return False

def _format_document(self, doc: Dict[str, Any]) -> str:
    """Format document for LLM prompt."""
    fields = doc.get('fields', {})
    lines = []
    for key, value in fields.items():
        if isinstance(value, str):
            lines.append(f"{key}: {value}")
    return "\n".join(lines)
```

---

## 🔴 CRITICAL FIX #5: Answer Template Validation

**File:** `backend/src/validation/conspiracy_validator.py`  
**Add new method:**

```python
def _validate_answer_template(self, mystery: ConspiracyMystery) -> bool:
    """Validate that answer template correctly extracts from premise."""
    
    if not mystery.answer_template:
        logger.warning("   ⚠️  No answer template")
        return False
    
    template = mystery.answer_template
    premise = mystery.premise
    
    logger.info("   Validating answer template extraction...")
    
    issues = []
    
    # Check WHO extraction
    if not self._fuzzy_contains(template.who, premise.who):
        issues.append(f"WHO mismatch: '{template.who}' not in '{premise.who[:50]}...'")
    
    # Check WHAT extraction  
    if not self._fuzzy_contains(template.what, premise.what):
        issues.append(f"WHAT mismatch: '{template.what}' not in '{premise.what[:50]}...'")
    
    # Check WHY extraction
    if not self._fuzzy_contains(template.why, premise.why):
        issues.append(f"WHY mismatch: '{template.why}' not in '{premise.why[:50]}...'")
    
    # Validate hash
    expected_hash = template.generate_hash()
    if template.combined_hash != expected_hash:
        issues.append(f"Hash mismatch: stored != calculated")
    
    if issues:
        logger.warning("   ❌ Answer template validation FAILED:")
        for issue in issues:
            logger.warning(f"      - {issue}")
        return False
    
    logger.info("   ✅ Answer template correctly extracted")
    return True

def _fuzzy_contains(self, extracted: str, source: str) -> bool:
    """Check if extracted text is contained in source (fuzzy)."""
    extracted_lower = extracted.lower().strip()
    source_lower = source.lower().strip()
    
    # Exact substring match
    if extracted_lower in source_lower:
        return True
    
    # Token overlap (at least 70%)
    extracted_tokens = set(extracted_lower.split())
    source_tokens = set(source_lower.split())
    overlap = len(extracted_tokens & source_tokens)
    
    return overlap >= len(extracted_tokens) * 0.7
```

**Update main validation method:**

```python
async def validate_conspiracy(
    self,
    mystery: ConspiracyMystery,
    config: Dict[str, Any] = None
) -> ValidationResult:
    """Validate conspiracy mystery."""
    
    # ... existing tests ...
    
    # NEW TEST: Answer template validation
    logger.info("TEST 0: Answer Template Validation")
    logger.info("-" * 60)
    template_valid = self._validate_answer_template(mystery)
    logger.info("")
    
    # Update final validation logic
    is_valid = (
        template_valid and  # NEW!
        single_llm_failed and
        multi_hop_succeeded and
        crypto_discoverable and
        all(answer_coverage.values())
    )
    
    if not template_valid:
        failures.append("Answer template extraction invalid")
```

---

## ⚠️ WARNING FIX #1: Use All Documents in Single-LLM Test

**File:** `backend/src/validation/conspiracy_validator.py`  
**Line:** 164

### Current Code:
```python
all_docs_text = "\n\n".join([
    f"Document {i+1}:\n{str(doc)}"
    for i, doc in enumerate(mystery.documents[:10])  # Only first 10!
])
```

### Fixed Code:
```python
# Use all documents (or random sample if too many)
max_docs = 20  # Reasonable limit for context window
docs_to_test = mystery.documents
if len(docs_to_test) > max_docs:
    import random
    docs_to_test = random.sample(mystery.documents, max_docs)
    logger.info(f"   Using random sample of {max_docs} documents")

all_docs_text = "\n\n".join([
    f"Document {i+1}:\n{str(doc)}"
    for i, doc in enumerate(docs_to_test)
])
```

---

## ⚠️ WARNING FIX #2: Better Answer Matching

**File:** `backend/src/validation/anti_automation.py`  
**Lines:** 196-198

### Current Code:
```python
who_found = any(name.lower() in response_lower for name in premise.who.split()[:3])
what_found = any(word.lower() in response_lower for word in premise.what.split()[:5])
```

### Fixed Code:
```python
# Better semantic matching
def check_semantic_match(response: str, target: str, threshold: float = 0.6) -> bool:
    """Check if response semantically contains target."""
    response_lower = response.lower()
    target_lower = target.lower()
    
    # Check full phrase
    if target_lower in response_lower:
        return True
    
    # Check token overlap
    response_tokens = set(response_lower.split())
    target_tokens = set(target_lower.split())
    
    # Remove stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at'}
    response_tokens -= stop_words
    target_tokens -= stop_words
    
    if not target_tokens:
        return False
    
    overlap = len(response_tokens & target_tokens)
    similarity = overlap / len(target_tokens)
    
    return similarity >= threshold

who_found = check_semantic_match(response, mystery.answer, threshold=0.7)
```

---

## Summary

These fixes address the critical shadow validation issues and ensure that:

1. ✅ Multi-hop validation actually tests LLM reasoning
2. ✅ Empty responses are treated as errors, not passes
3. ✅ Arkiv imports work correctly
4. ✅ Crypto keys are tested for actual discoverability
5. ✅ Answer templates are validated
6. ✅ All documents are used in testing
7. ✅ Answer matching is more accurate

**Estimated time to implement:** 1-2 days of focused development

