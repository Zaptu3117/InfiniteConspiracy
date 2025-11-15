#!/usr/bin/env python3
"""Debug validation to see what's happening."""

import asyncio
import logging
import sys
import os
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils import CerebrasClient
from models.conspiracy import *

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def debug_single_step():
    """Debug a single validation step."""
    
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        logger.error("CEREBRAS_API_KEY not set")
        return
    
    # Load mystery
    conspiracies_dir = Path("outputs/conspiracies")
    mystery_dirs = sorted(conspiracies_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    mystery_file = mystery_dirs[0] / "mystery.json"
    
    logger.info(f"Loading: {mystery_dirs[0].name}\n")
    
    with open(mystery_file) as f:
        data = json.load(f)
    
    # Get first non-red-herring subgraph with inference nodes
    for sg_data in data['subgraphs']:
        if sg_data['is_red_herring'] or not sg_data.get('inference_nodes'):
            continue
        
        # Get first inference node
        inf_node = sg_data['inference_nodes'][0]
        doc_ids = inf_node.get('required_document_ids', [])
        
        if not doc_ids:
            continue
        
        logger.info("="*60)
        logger.info(f"Subgraph: {sg_data['subgraph_id']}")
        logger.info(f"Inference: {inf_node['inference'][:100]}...")
        logger.info(f"Required docs: {doc_ids}")
        logger.info("")
        
        # Get the documents
        docs = [d for d in data['documents'] if d.get('document_id') in doc_ids]
        logger.info(f"Found {len(docs)} documents\n")
        
        # Format for LLM (same as validator)
        def format_doc(doc):
            fields = doc.get('fields', {})
            lines = [f"Document ID: {doc.get('document_id', 'unknown')}"]
            
            for key, value in fields.items():
                if isinstance(value, str) and value.strip():
                    lines.append(f"{key}: {value}")
                elif isinstance(value, list) and value:
                    lines.append(f"{key}:")
                    for i, item in enumerate(value[:20]):
                        if isinstance(item, dict):
                            item_str = ", ".join(f"{k}={v}" for k, v in item.items())
                            lines.append(f"  [{i+1}] {item_str}")
                        else:
                            lines.append(f"  [{i+1}] {item}")
                    if len(value) > 20:
                        lines.append(f"  ... and {len(value) - 20} more entries")
                elif isinstance(value, dict) and value:
                    lines.append(f"{key}:")
                    for k, v in value.items():
                        lines.append(f"  {k}: {v}")
            
            return "\n".join(lines)
        
        docs_text = "\n\n".join([format_doc(doc) for doc in docs])
        
        logger.info("Documents content:")
        logger.info(docs_text[:500] + "...")
        logger.info("")
        
        # Make inference
        llm = CerebrasClient(api_key)
        
        prompt = f"""You are investigating a conspiracy. Analyze these documents and extract relevant information.

DOCUMENTS:
{docs_text}

TASK: Based on the documents, explain what you can determine about:
{inf_node['inference']}

Provide a clear, specific answer with details from the documents. If the documents don't support this conclusion, explain why.

ANSWER:"""
        
        logger.info("="*60)
        logger.info("Calling LLM for inference...")
        response = await llm.generate(prompt, temperature=0.3, max_tokens=2000)
        
        logger.info(f"\nLLM Response:\n{response}")
        logger.info("")
        
        # Now test judgment
        logger.info("="*60)
        logger.info("Calling LLM as judge...")
        
        assessment_prompt = f"""You are assessing whether an investigator's finding matches the expected discovery.

EXPECTED DISCOVERY: {inf_node['inference']}

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
        
        judgment = await llm.generate(assessment_prompt, temperature=0.1, max_tokens=2000)
        
        logger.info(f"\nJudge Response: '{judgment}' (length: {len(judgment)})")
        logger.info(f"Repr: {repr(judgment)}")
        if judgment and judgment.strip():
            logger.info(f"Match: {'YES' in judgment.upper()}")
        else:
            logger.info("Match: FAILED (empty response)")
            
            # Test with a simpler prompt to see if API works
            logger.info("\n🔧 Testing API with simple prompt...")
            simple_test = await llm.generate("Say 'HELLO'.", temperature=0.1, max_tokens=5)
            logger.info(f"   Simple test response: '{simple_test}' (length: {len(simple_test)})")
        logger.info("")
        
        break

if __name__ == "__main__":
    asyncio.run(debug_single_step())

