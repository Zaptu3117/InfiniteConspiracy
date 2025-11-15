#!/usr/bin/env python3
"""
Demonstration of Shadow Validation Issue

This script shows how the current validation appears to work
but doesn't actually test what it claims to test.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.conspiracy import (
    ConspiracyMystery,
    ConspiracyPremise,
    PoliticalContext,
    SubGraph,
    EvidenceType,
    AnswerDimension
)


def create_broken_mystery():
    """
    Create a mystery that looks valid structurally
    but is actually unsolvable.
    """
    
    # Create a premise
    premise = ConspiracyPremise(
        who="Agent Smith",
        what="Operation Broken",
        why="World domination",
        how="Secret technology",
        conspiracy_name="The Broken Conspiracy"
    )
    
    # Create political context
    context = PoliticalContext(
        world_name="Test World"
    )
    
    # Create sub-graphs that are structurally complete
    # but have NO actual evidence or documents
    subgraph1 = SubGraph(
        subgraph_id="sg1",
        subgraph_type=EvidenceType.IDENTITY,
        is_complete=True,  # Claims to be complete
        is_red_herring=False,
        contributes_to=AnswerDimension.WHO,
        hop_count=3,
        conclusion="Identity chain leads to Agent Smith"
    )
    # NOTE: No evidence_nodes, no inference_nodes!
    
    subgraph2 = SubGraph(
        subgraph_id="sg2",
        subgraph_type=EvidenceType.PSYCHOLOGICAL,
        is_complete=True,  # Claims to be complete
        is_red_herring=False,
        contributes_to=AnswerDimension.WHY,
        hop_count=2,
        conclusion="Motivation is world domination"
    )
    # NOTE: No evidence_nodes, no inference_nodes!
    
    # Create mystery with empty documents
    mystery = ConspiracyMystery(
        mystery_id="broken_mystery_001",
        political_context=context,
        premise=premise,
        subgraphs=[subgraph1, subgraph2],
        documents=[],  # NO DOCUMENTS!
        difficulty=7
    )
    
    return mystery


def simulate_current_validation(mystery):
    """
    Simulate what the current _test_multi_hop() function does.
    """
    print("="*60)
    print("CURRENT VALIDATION (Shadow Validation)")
    print("="*60)
    print()
    
    # This is what the code actually does:
    complete_chains = [sg for sg in mystery.subgraphs if sg.is_complete and not sg.is_red_herring]
    
    print(f"Checking sub-graphs...")
    print(f"  Total sub-graphs: {len(mystery.subgraphs)}")
    print(f"  Complete chains: {len(complete_chains)}")
    print()
    
    if not complete_chains:
        print("❌ VALIDATION FAILED: No complete evidence chains")
        return False
    
    # Check dimensions
    dimensions_covered = set()
    for sg in complete_chains:
        if sg.contributes_to:
            dimensions_covered.add(sg.contributes_to)
    
    print(f"Dimensions covered: {len(dimensions_covered)}/4")
    for dim in dimensions_covered:
        print(f"  ✅ {dim.value.upper()}")
    print()
    
    print("✅ VALIDATION PASSED - Mystery appears solvable!")
    print()
    print("BUT WAIT... let's check what's actually in the mystery:")
    print()
    
    return True


def reality_check(mystery):
    """
    Check what's actually in the mystery.
    """
    print("="*60)
    print("REALITY CHECK")
    print("="*60)
    print()
    
    issues = []
    
    # Check documents
    print(f"Documents: {len(mystery.documents)}")
    if len(mystery.documents) == 0:
        issues.append("❌ NO DOCUMENTS - Players have nothing to read!")
    print()
    
    # Check evidence nodes
    total_evidence = sum(len(sg.evidence_nodes) for sg in mystery.subgraphs)
    print(f"Evidence nodes: {total_evidence}")
    if total_evidence == 0:
        issues.append("❌ NO EVIDENCE - Sub-graphs are empty shells!")
    print()
    
    # Check inference nodes
    total_inferences = sum(len(sg.inference_nodes) for sg in mystery.subgraphs)
    print(f"Inference nodes: {total_inferences}")
    if total_inferences == 0:
        issues.append("❌ NO INFERENCES - No reasoning chain to follow!")
    print()
    
    # Check crypto keys
    print(f"Crypto keys: {len(mystery.crypto_keys)}")
    print()
    
    if issues:
        print("="*60)
        print("ACTUAL VALIDATION RESULT")
        print("="*60)
        print()
        for issue in issues:
            print(issue)
        print()
        print("🚨 THIS MYSTERY IS COMPLETELY UNSOLVABLE!")
        print()
        print("The structural validation passed, but there's no actual content.")
        print("This is the 'Shadow Validation' problem.")
        print()


def demonstrate_proper_validation():
    """
    Show what proper validation should do.
    """
    print("="*60)
    print("PROPER VALIDATION (What Should Happen)")
    print("="*60)
    print()
    
    print("1. Check structural completeness ✓")
    print("   - Sub-graphs exist")
    print("   - Dimensions covered")
    print()
    
    print("2. Check content exists:")
    print("   - Evidence nodes populated")
    print("   - Inference nodes created")
    print("   - Documents generated")
    print("   - Crypto keys with hints")
    print()
    
    print("3. Test actual solvability with LLM:")
    print("   - Give LLM the documents")
    print("   - Ask sub-questions from inference chain")
    print("   - Verify LLM can make each inference")
    print("   - Check if final answer is reached")
    print()
    
    print("4. Validate crypto discoverability:")
    print("   - Find hint documents")
    print("   - Test if LLM can infer key")
    print("   - Verify decryption works")
    print()


def main():
    """Main demonstration."""
    print()
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "SHADOW VALIDATION DEMONSTRATION" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    print()
    
    # Create a structurally valid but actually broken mystery
    mystery = create_broken_mystery()
    
    # Run current validation (will pass!)
    current_result = simulate_current_validation(mystery)
    
    # Show what's actually wrong
    reality_check(mystery)
    
    # Show what proper validation looks like
    demonstrate_proper_validation()
    
    print("="*60)
    print("CONCLUSION")
    print("="*60)
    print()
    print("The current validation system checks STRUCTURE but not FUNCTION.")
    print()
    print("A mystery can:")
    print("  ✅ Pass all structural checks")
    print("  ✅ Have complete sub-graphs")
    print("  ✅ Cover all answer dimensions")
    print()
    print("But still be:")
    print("  ❌ Completely empty (no documents)")
    print("  ❌ Impossible to solve (no evidence)")
    print("  ❌ Broken (no reasoning chain)")
    print()
    print("This is why we need FUNCTIONAL validation, not just structural.")
    print()


if __name__ == "__main__":
    main()

