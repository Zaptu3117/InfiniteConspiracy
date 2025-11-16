"""Test script to generate a conspiracy with the refactored system."""

import asyncio
import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from narrative.conspiracy.conspiracy_pipeline import ConspiracyPipeline
from utils.llm_clients import CerebrasClient


async def test_conspiracy_generation():
    """Generate a conspiracy and verify answers are discoverable."""
    
    print("="*80)
    print("TESTING REFACTORED CONSPIRACY GENERATION")
    print("="*80)
    print()
    
    # Initialize LLM client
    cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
    if not cerebras_api_key:
        print("❌ CEREBRAS_API_KEY environment variable not set")
        return False
    
    llm = CerebrasClient(api_key=cerebras_api_key)
    
    # Initialize pipeline
    pipeline = ConspiracyPipeline(llm_client=llm, config={})
    
    # Generate conspiracy
    print("Generating conspiracy mystery...")
    print()
    
    mystery = await pipeline.generate_conspiracy_mystery(
        difficulty=5,
        num_documents=20,
        conspiracy_type="occult"
    )
    
    print()
    print("="*80)
    print("GENERATION COMPLETE - VERIFYING DISCOVERABILITY")
    print("="*80)
    print()
    
    # Extract answers
    answer_template = mystery.answer_template
    if not answer_template:
        print("❌ No answer template found!")
        return False
    
    who_answer = answer_template.who
    what_answer = answer_template.what
    why_answer = answer_template.why
    how_answer = answer_template.how
    
    print(f"WHO: \"{who_answer}\"")
    print(f"WHAT: \"{what_answer}\"")
    print(f"WHY: \"{why_answer}\"")
    print(f"HOW: \"{how_answer}\"")
    print()
    
    # Check questions
    questions = mystery.questions
    if questions:
        print("QUESTIONS GENERATED:")
        for key, question in questions.items():
            print(f"  {key.upper()}: {question}")
        print()
    else:
        print("⚠️  No questions generated!")
        print()
    
    # Search documents for answers
    print("="*80)
    print("CHARACTER DIVERSITY CHECK")
    print("="*80)
    print(f"Total characters: {len(mystery.characters)}")
    primary_chars = [c for c in mystery.characters if c.get("is_primary")]
    secondary_chars = [c for c in mystery.characters if c.get("involvement_level") == "conspirator"]
    innocent_chars = [c for c in mystery.characters if c.get("involvement_level") == "innocent"]
    print(f"  Primary conspirators: {len(primary_chars)}")
    print(f"  Secondary conspirators: {len(secondary_chars)}")
    print(f"  Innocent characters: {len(innocent_chars)}")
    if primary_chars:
        print(f"  Primary name: {primary_chars[0]['name']}")
    print()
    
    print("="*80)
    print("SEARCHING DOCUMENTS FOR ANSWERS")
    print("="*80)
    print()
    
    who_count = 0
    what_count = 0
    why_count = 0
    how_count = 0
    
    who_docs = []
    what_docs = []
    why_docs = []
    how_docs = []
    
    for i, doc in enumerate(mystery.documents):
        doc_text = json.dumps(doc).lower()
        doc_name = doc.get("document_name", f"doc_{i}")
        
        if who_answer.lower() in doc_text:
            who_count += 1
            who_docs.append(doc_name)
        
        if what_answer.lower() in doc_text:
            what_count += 1
            what_docs.append(doc_name)
        
        if why_answer.lower() in doc_text:
            why_count += 1
            why_docs.append(doc_name)
        
        if how_answer.lower() in doc_text:
            how_count += 1
            how_docs.append(doc_name)
    
    print(f"WHO \"{who_answer}\" found in {who_count} documents")
    if who_docs[:3]:
        print(f"  First 3: {', '.join(who_docs[:3])}")
    print()
    
    print(f"WHAT \"{what_answer}\" found in {what_count} documents")
    if what_docs[:3]:
        print(f"  First 3: {', '.join(what_docs[:3])}")
    print()
    
    print(f"WHY \"{why_answer}\" found in {why_count} documents")
    if why_docs[:3]:
        print(f"  First 3: {', '.join(why_docs[:3])}")
    print()
    
    print(f"HOW \"{how_answer}\" found in {how_count} documents")
    if how_docs[:3]:
        print(f"  First 3: {', '.join(how_docs[:3])}")
    print()
    
    # Evaluate discoverability
    print("="*80)
    print("DISCOVERABILITY ASSESSMENT")
    print("="*80)
    print()
    
    all_discoverable = True
    
    if who_count >= 1:
        containment_status = "✅ EXCELLENT" if who_count <= 3 else "⚠️  TOO MANY"
        print(f"✅ WHO: DISCOVERABLE ({who_count} occurrences) {containment_status}")
        if who_count > 3:
            all_discoverable = False
    else:
        print(f"❌ WHO: NOT DISCOVERABLE")
        all_discoverable = False
    
    if what_count >= 1:
        containment_status = "✅ PERFECT" if what_count == 1 else ("✅ GOOD" if what_count <= 3 else "⚠️  TOO MANY")
        print(f"✅ WHAT: DISCOVERABLE ({what_count} occurrences) {containment_status}")
        if what_count > 5:
            all_discoverable = False
    else:
        print(f"❌ WHAT: NOT DISCOVERABLE")
        all_discoverable = False
    
    if why_count >= 1:
        print(f"✅ WHY: DISCOVERABLE ({why_count} occurrences)")
    else:
        print(f"❌ WHY: NOT DISCOVERABLE")
        all_discoverable = False
    
    if how_count >= 1:
        print(f"✅ HOW: DISCOVERABLE ({how_count} occurrences)")
    else:
        print(f"❌ HOW: NOT DISCOVERABLE")
        all_discoverable = False
    
    print()
    
    # Overall result
    print("="*80)
    if all_discoverable:
        print("✅ SUCCESS: ALL ANSWERS ARE DISCOVERABLE!")
    else:
        print("❌ FAILURE: SOME ANSWERS ARE NOT DISCOVERABLE")
    print("="*80)
    print()
    
    # Try to load validation result from saved file
    try:
        # Find the mystery folder
        outputs_dir = "outputs/conspiracies"
        import re
        conspiracy_name = mystery.premise.conspiracy_name
        safe_name = re.sub(r'[^\w\s-]', '', conspiracy_name).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        short_uuid = mystery.mystery_id[:8]
        folder_name = f"{safe_name}_{short_uuid}"
        
        validation_file = os.path.join(outputs_dir, folder_name, "validation.json")
        if os.path.exists(validation_file):
            with open(validation_file) as f:
                validation_data = json.load(f)
            
            print("VALIDATION RESULT (from saved file):")
            print(f"  Valid: {validation_data.get('is_valid')}")
            print(f"  Reason: {validation_data.get('reason')}")
            print(f"  WHO Solvable: {validation_data.get('who_solvable')}")
            print(f"  WHAT Solvable: {validation_data.get('what_solvable')}")
            print(f"  WHY Solvable: {validation_data.get('why_solvable')}")
            print(f"  HOW Solvable: {validation_data.get('how_solvable')}")
            print()
    except Exception as e:
        print(f"⚠️  Could not load validation result: {e}")
        print()
    
    return all_discoverable


if __name__ == "__main__":
    result = asyncio.run(test_conspiracy_generation())
    sys.exit(0 if result else 1)

