"""
Test the new three-layer architecture for document generation.

This test verifies:
1. Evidence fact extraction works
2. Document narrative planning enforces containment
3. Document rendering produces valid documents
4. WHO answer appears in ≤3 documents
5. WHAT answer appears in exactly 1 document
"""

import asyncio
import sys
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / "src"))

from narrative.conspiracy.conspiracy_pipeline import ConspiracyPipeline
from utils.llm_clients import CerebrasClient
import os


async def test_new_architecture():
    """Test the new architecture."""
    print("="*70)
    print("TESTING NEW THREE-LAYER ARCHITECTURE")
    print("="*70)
    print()
    
    # Initialize LLM client
    cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
    if not cerebras_api_key:
        print("❌ CEREBRAS_API_KEY environment variable not set")
        return False
    
    llm_client = CerebrasClient(api_key=cerebras_api_key)
    
    # Simple config
    config = {
        "political_context": {},
        "conspiracy": {},
        "document_generation": {
            "temperature": 0.7,
            "max_tokens": 3000
        }
    }
    
    # Initialize pipeline
    pipeline = ConspiracyPipeline(
        llm_client=llm_client,
        config=config
    )
    
    print("Generating conspiracy with new architecture...")
    print()
    
    # Generate conspiracy
    mystery = await pipeline.generate_conspiracy_mystery(
        difficulty=7,
        num_documents=15,
        conspiracy_type="occult"
    )
    
    print()
    print("="*70)
    print("GENERATION COMPLETE - ANALYZING RESULTS")
    print("="*70)
    print()
    
    # Extract answers
    who_answer = mystery.answer_template.who
    what_answer = mystery.answer_template.what
    why_answer = mystery.answer_template.why
    how_answer = mystery.answer_template.how
    
    print(f"ANSWERS:")
    print(f"  WHO: {who_answer}")
    print(f"  WHAT: {what_answer}")
    print(f"  WHY: {why_answer}")
    print(f"  HOW: {how_answer}")
    print()
    
    # Count occurrences in documents
    who_count = 0
    what_count = 0
    why_count = 0
    how_count = 0
    
    who_docs = []
    what_docs = []
    why_docs = []
    how_docs = []
    
    for doc in mystery.documents:
        doc_str = json.dumps(doc).lower()
        
        if who_answer.lower() in doc_str:
            who_count += 1
            who_docs.append(doc.get("document_id", "unknown"))
        
        if what_answer.lower() in doc_str:
            what_count += 1
            what_docs.append(doc.get("document_id", "unknown"))
        
        if why_answer.lower() in doc_str:
            why_count += 1
            why_docs.append(doc.get("document_id", "unknown"))
        
        if how_answer.lower() in doc_str:
            how_count += 1
            how_docs.append(doc.get("document_id", "unknown"))
    
    print("="*70)
    print("CONTAINMENT ANALYSIS")
    print("="*70)
    print()
    
    print(f"WHO answer '{who_answer}' appears in: {who_count} documents")
    print(f"  Documents: {who_docs}")
    print(f"  ✅ PASS" if who_count <= 3 else f"  ❌ FAIL - Expected ≤3, got {who_count}")
    print()
    
    print(f"WHAT answer '{what_answer}' appears in: {what_count} documents")
    print(f"  Documents: {what_docs}")
    print(f"  ✅ PASS" if what_count == 1 else f"  ❌ FAIL - Expected 1, got {what_count}")
    print()
    
    print(f"WHY answer '{why_answer}' appears in: {why_count} documents")
    print(f"  Documents: {why_docs}")
    print(f"  ✅ PASS" if why_count >= 1 else f"  ❌ FAIL - Expected ≥1, got {why_count}")
    print()
    
    print(f"HOW answer '{how_answer}' appears in: {how_count} documents")
    print(f"  Documents: {how_docs}")
    print(f"  ✅ PASS" if how_count >= 1 else f"  ❌ FAIL - Expected ≥1, got {how_count}")
    print()
    
    # Overall assessment
    print("="*70)
    print("OVERALL ASSESSMENT")
    print("="*70)
    print()
    
    all_pass = (
        who_count <= 3 and
        what_count == 1 and
        why_count >= 1 and
        how_count >= 1
    )
    
    if all_pass:
        print("✅ ALL TESTS PASSED - New architecture working correctly!")
    else:
        print("❌ SOME TESTS FAILED - See details above")
    
    print()
    print(f"Total documents generated: {len(mystery.documents)}")
    print(f"Total subgraphs: {len(mystery.subgraphs)}")
    print(f"Total characters: {len(mystery.characters)}")
    
    return all_pass


if __name__ == "__main__":
    success = asyncio.run(test_new_architecture())
    sys.exit(0 if success else 1)

