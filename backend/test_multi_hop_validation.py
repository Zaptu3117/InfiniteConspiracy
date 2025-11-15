#!/usr/bin/env python3
"""Test multi-hop validation with real LLM calls."""

import asyncio
import logging
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils import CerebrasClient
from validation.conspiracy_validator import ConspiracyValidator
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def test_validation():
    """Test validation on a generated mystery."""
    
    # Load API key
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        logger.error("❌ CEREBRAS_API_KEY not set")
        logger.error("   Set it with: export CEREBRAS_API_KEY=your_key")
        return
    
    # Find a generated mystery
    conspiracies_dir = Path("outputs/conspiracies")
    if not conspiracies_dir.exists():
        logger.error("❌ No mysteries found. Generate one first.")
        logger.error("   Run: uv run python test_conspiracy_full.py")
        return
    
    # Load NEWEST mystery (sorted by modification time)
    mystery_dirs = sorted([d for d in conspiracies_dir.iterdir() if d.is_dir()], 
                         key=lambda x: x.stat().st_mtime, reverse=True)
    if not mystery_dirs:
        logger.error("❌ No mysteries in outputs/conspiracies")
        return
    
    mystery_file = mystery_dirs[0] / "mystery.json"
    logger.info(f"📂 Loading NEWEST mystery: {mystery_dirs[0].name}")
    
    with open(mystery_file, 'r') as f:
        mystery_data = json.load(f)
    
    # Recreate mystery object with proper nested structures
    from models.conspiracy import (
        ConspiracyMystery, 
        ConspiracyPremise,
        PoliticalContext,
        SubGraph,
        EvidenceType,
        AnswerDimension,
        EvidenceNode,
        InferenceNode,
        CryptoKey,
        DocumentAssignment,
        ImageClue,
        MysteryAnswer
    )
    
    # Reconstruct political context
    political_context = PoliticalContext(**mystery_data['political_context'])
    
    # Reconstruct premise
    premise = ConspiracyPremise(**mystery_data['premise'])
    
    # Reconstruct answer template if exists
    answer_template = None
    if mystery_data.get('answer_template'):
        answer_template = MysteryAnswer(**mystery_data['answer_template'])
    
    # Reconstruct subgraphs
    subgraphs = []
    for sg_data in mystery_data['subgraphs']:
        # Reconstruct evidence nodes
        evidence_nodes = [EvidenceNode(**en) for en in sg_data.get('evidence_nodes', [])]
        
        # Reconstruct inference nodes
        inference_nodes = []
        for in_data in sg_data.get('inference_nodes', []):
            # Handle contributes_to enum
            if in_data.get('contributes_to'):
                in_data['contributes_to'] = AnswerDimension(in_data['contributes_to'])
            inference_nodes.append(InferenceNode(**in_data))
        
        # Reconstruct subgraph
        sg_data['subgraph_type'] = EvidenceType(sg_data['subgraph_type'])
        if sg_data.get('contributes_to'):
            sg_data['contributes_to'] = AnswerDimension(sg_data['contributes_to'])
        sg_data['evidence_nodes'] = evidence_nodes
        sg_data['inference_nodes'] = inference_nodes
        
        subgraphs.append(SubGraph(**sg_data))
    
    # Reconstruct crypto keys
    crypto_keys = [CryptoKey(**ck) for ck in mystery_data.get('crypto_keys', [])]
    
    # Reconstruct document assignments
    doc_assignments = [DocumentAssignment(**da) for da in mystery_data.get('document_assignments', [])]
    
    # Reconstruct image clues
    image_clues = [ImageClue(**ic) for ic in mystery_data.get('image_clues', [])]
    
    # Create full mystery object
    mystery = ConspiracyMystery(
        mystery_id=mystery_data['mystery_id'],
        political_context=political_context,
        premise=premise,
        answer_template=answer_template,
        subgraphs=subgraphs,
        crypto_keys=crypto_keys,
        document_assignments=doc_assignments,
        image_clues=image_clues,
        characters=mystery_data.get('characters', []),
        documents=mystery_data.get('documents', []),
        difficulty=mystery_data.get('difficulty', 5),
        created_at=mystery_data.get('created_at')
    )
    
    logger.info(f"   Conspiracy: {mystery.premise.conspiracy_name}")
    logger.info(f"   Documents: {len(mystery.documents)}")
    logger.info(f"   Sub-graphs: {len(mystery.subgraphs)}")
    
    # Create validator
    llm = CerebrasClient(api_key)
    validator = ConspiracyValidator(llm)
    
    # Run validation
    logger.info("\n" + "="*60)
    logger.info("TESTING MULTI-HOP VALIDATION")
    logger.info("="*60 + "\n")
    
    try:
        result = await validator.validate_conspiracy(mystery)
        
        logger.info("\n" + "="*60)
        logger.info("RESULTS")
        logger.info("="*60)
        logger.info(f"Valid: {result.is_valid}")
        logger.info(f"Multi-hop succeeded: {result.multi_hop_succeeded}")
        logger.info(f"Reason: {result.reason}")
        logger.info("")
        
        if result.multi_hop_succeeded:
            logger.info("✅ SUCCESS: Mystery is solvable with guided reasoning!")
        else:
            logger.info("❌ FAILED: Mystery has issues with multi-hop reasoning")
    
    except Exception as e:
        logger.error(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_validation())

