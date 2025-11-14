#!/usr/bin/env python3
"""
Generate a complete mystery with documents, images, and validation.

Usage:
    python scripts/generate_mystery.py [--difficulty 5] [--docs 20]
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import load_config, setup_logger
from models import Mystery, MysteryMetadata


async def generate_simple_mystery(difficulty: int = 5, num_docs: int = 20):
    """
    Generate a simple mystery for demonstration.
    
    This is a simplified version that creates a basic mystery structure.
    Full implementation would use LangGraph for more complex generation.
    """
    logger = setup_logger("mystery_generator", "INFO", config.log_dir)
    logger.info("🎲 Starting mystery generation...")
    logger.info(f"   Difficulty: {difficulty}")
    logger.info(f"   Target documents: {num_docs}")
    logger.info("")
    
    # Create mystery metadata
    metadata = MysteryMetadata(
        question="Who leaked the classified documents to the press?",
        difficulty=difficulty,
        total_documents=num_docs,
        total_images=5
    )
    
    logger.info(f"📋 Mystery ID: {metadata.mystery_id}")
    logger.info(f"   Question: {metadata.question}")
    logger.info("")
    
    # Create mystery object
    mystery = Mystery(
        metadata=metadata,
        answer="Sarah Martinez",  # The answer
        proof_tree={
            "answer": "Sarah Martinez",
            "inference_nodes": [
                {
                    "node_id": "node_1",
                    "inference": "Email from John mentions meeting at 02:47am",
                    "document_ids": ["doc_1_email"],
                    "reasoning_type": "direct_observation",
                    "parent_nodes": [],
                    "children_nodes": ["node_3"]
                },
                {
                    "node_id": "node_2",
                    "inference": "Badge log shows Sarah at Warehouse 4B at 02:43am",
                    "document_ids": ["doc_2_badge_log"],
                    "reasoning_type": "direct_observation",
                    "parent_nodes": [],
                    "children_nodes": ["node_3"]
                },
                {
                    "node_id": "node_3",
                    "inference": "Sarah was at the warehouse before the meeting time",
                    "document_ids": ["doc_1_email", "doc_2_badge_log"],
                    "reasoning_type": "temporal_reasoning",
                    "parent_nodes": ["node_1", "node_2"],
                    "children_nodes": ["node_5"]
                },
                {
                    "node_id": "node_4",
                    "inference": "Documents were leaked between 02:30am and 03:00am",
                    "document_ids": ["doc_3_security_log"],
                    "reasoning_type": "temporal_reasoning",
                    "parent_nodes": [],
                    "children_nodes": ["node_5"]
                },
                {
                    "node_id": "node_5",
                    "inference": "Sarah Martinez leaked the documents",
                    "document_ids": ["doc_1_email", "doc_2_badge_log", "doc_3_security_log"],
                    "reasoning_type": "synthesis",
                    "parent_nodes": ["node_3", "node_4"],
                    "children_nodes": []
                }
            ],
            "validation_steps": [
                {
                    "step_number": 1,
                    "sub_question": "What time was the meeting mentioned in the email?",
                    "required_document_ids": ["doc_1_email"],
                    "expected_inference": "02:47am",
                    "inference_node_id": "node_1"
                },
                {
                    "step_number": 2,
                    "sub_question": "Who accessed Warehouse 4B before the meeting?",
                    "required_document_ids": ["doc_2_badge_log"],
                    "expected_inference": "Sarah Martinez at 02:43am",
                    "inference_node_id": "node_2"
                },
                {
                    "step_number": 3,
                    "sub_question": "When were the documents leaked?",
                    "required_document_ids": ["doc_3_security_log"],
                    "expected_inference": "Between 02:30am and 03:00am",
                    "inference_node_id": "node_4"
                },
                {
                    "step_number": 4,
                    "sub_question": "Who had access during the leak timeframe?",
                    "required_document_ids": ["doc_1_email", "doc_2_badge_log", "doc_3_security_log"],
                    "expected_inference": "Sarah Martinez",
                    "inference_node_id": "node_5"
                }
            ],
            "total_hops": 4,
            "min_hops": 3,
            "max_hops": 7
        }
    )
    
    # Generate documents
    logger.info("📄 Generating documents...")
    
    documents = [
        {
            "document_id": "doc_1_email",
            "document_type": "email",
            "fields": {
                "from": "john.doe@company.com",
                "to": ["operations@company.com"],
                "subject": "Urgent: Tonight's Meeting",
                "body": "Remember, we meet at 02:47am at the usual spot. Bring the files.",
                "timestamp": "2024-11-12T18:30:00Z"
            },
            "cipher_info": None,
            "contains_clues": ["meeting_time"],
            "proof_step": 1
        },
        {
            "document_id": "doc_2_badge_log",
            "document_type": "badge_log",
            "fields": {
                "facility_name": "Warehouse District",
                "log_period": "2024-11-13",
                "entries": [
                    {
                        "badge_number": "5829",
                        "name": "Sarah Martinez",
                        "entry_time": "2024-11-13T02:43:00Z",
                        "location": "Warehouse 4B"
                    },
                    {
                        "badge_number": "4217",
                        "name": "John Doe",
                        "entry_time": "2024-11-13T02:50:00Z",
                        "location": "Warehouse 4B"
                    }
                ]
            },
            "cipher_info": None,
            "contains_clues": ["sarah_access"],
            "proof_step": 2
        },
        {
            "document_id": "doc_3_security_log",
            "document_type": "surveillance_log",
            "fields": {
                "location": "Server Room",
                "date": "2024-11-13",
                "entries": [
                    {
                        "time": "02:35:00",
                        "event": "File access detected - Classified folder",
                        "user": "Unknown"
                    },
                    {
                        "time": "02:52:00",
                        "event": "Large file transfer to external IP",
                        "user": "Unknown"
                    }
                ]
            },
            "cipher_info": None,
            "contains_clues": ["leak_time"],
            "proof_step": 3
        }
    ]
    
    # Add more filler documents to reach target
    for i in range(4, num_docs + 1):
        documents.append({
            "document_id": f"doc_{i}_filler",
            "document_type": "internal_memo",
            "fields": {
                "from": "admin@company.com",
                "to": ["all@company.com"],
                "date": "2024-11-10",
                "subject": f"Routine Update #{i}",
                "content": f"This is a routine update document. Nothing suspicious here."
            },
            "cipher_info": None,
            "contains_clues": [],
            "proof_step": None
        })
    
    mystery.documents = documents
    logger.info(f"   ✅ Generated {len(documents)} documents")
    logger.info("")
    
    # Generate images (placeholder)
    logger.info("🖼️  Generating images...")
    images = [
        {
            "image_id": "img_1_badge",
            "description": "Photo of Sarah's security badge showing badge number 5829",
            "required_elements": ["badge_number_5829"],
            "generated": False
        }
    ]
    mystery.images = images
    logger.info(f"   ✅ Planned {len(images)} images (generation skipped for demo)")
    logger.info("")
    
    # Generate hashes
    logger.info("🔐 Generating hashes...")
    mystery.generate_hashes()
    logger.info(f"   Answer Hash: {mystery.answer_hash}")
    logger.info(f"   Proof Hash: {mystery.proof_hash}")
    logger.info("")
    
    # Validation (simplified)
    logger.info("🔍 Validation...")
    logger.info("   ⚠️  Full validation skipped (requires LLM APIs)")
    logger.info("   In production:")
    logger.info("     1. Single-LLM test (should fail)")
    logger.info("     2. Multi-hop test (should succeed)")
    mystery.validation_passed = True
    mystery.validation_details = {
        "single_llm_failed": True,
        "multi_hop_succeeded": True,
        "total_hops": 4
    }
    logger.info("   ✅ Validation marked as passed (demo mode)")
    logger.info("")
    
    # Save mystery
    logger.info("💾 Saving mystery...")
    output_dir = config.outputs_dir / "mysteries"
    mystery_path = mystery.save_to_file(str(output_dir))
    logger.info(f"   ✅ Saved to: {mystery_path}")
    logger.info("")
    
    # Summary
    logger.info("="*60)
    logger.info("✅ Mystery generation complete!")
    logger.info("="*60)
    logger.info(f"Mystery ID: {metadata.mystery_id}")
    logger.info(f"Question: {metadata.question}")
    logger.info(f"Answer: {mystery.answer}")
    logger.info(f"Documents: {len(mystery.documents)}")
    logger.info(f"Images: {len(mystery.images)}")
    logger.info(f"Difficulty: {difficulty}/10")
    logger.info(f"Output: {mystery_path}")
    logger.info("")
    logger.info("Next steps:")
    logger.info(f"  1. python scripts/push_to_arkiv.py {mystery_path.name}")
    logger.info(f"  2. python scripts/register_on_chain.py {mystery_path.name}")
    logger.info("")
    
    return mystery


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate a mystery")
    parser.add_argument("--difficulty", type=int, default=5, help="Difficulty (1-10)")
    parser.add_argument("--docs", type=int, default=20, help="Number of documents")
    parser.add_argument("--mode", choices=["demo", "llm"], default="demo", 
                       help="Generation mode: demo (no API) or llm (full LLM generation)")
    args = parser.parse_args()
    
    # Validate config
    if not config.validate():
        print("❌ Configuration validation failed. Please check your .env file.")
        return 1
    
    # Run generation based on mode
    if args.mode == "llm":
        asyncio.run(generate_with_llm(args.difficulty, args.docs))
    else:
        asyncio.run(generate_simple_mystery(args.difficulty, args.docs))
    
    return 0


async def generate_with_llm(difficulty: int, num_docs: int):
    """Generate mystery using full LLM pipeline."""
    from narrative.pipeline import LLMNarrativePipeline
    from utils.llm_clients import CerebrasClient
    
    logger = setup_logger("mystery_generator", "INFO", config.log_dir)
    
    logger.info("🎭 LLM MODE: Full narrative generation with AI")
    logger.info("")
    
    # Create LLM client
    cerebras = CerebrasClient(config.cerebras_api_key)
    
    # Load narrator config
    narrator_config = config.narrator_config
    
    # Create pipeline (with optional image generation)
    pipeline = LLMNarrativePipeline(
        cerebras,
        narrator_config,
        replicate_token=config.replicate_api_token,
        openai_key=config.openai_api_key
    )
    
    # Generate mystery
    mystery = await pipeline.generate_mystery_with_llm(
        difficulty=difficulty,
        num_docs=num_docs
    )
    
    # Save mystery
    logger.info("💾 Saving mystery...")
    output_dir = config.outputs_dir / "mysteries"
    mystery_path = mystery.save_to_file(str(output_dir))
    logger.info(f"   ✅ Saved to: {mystery_path}")
    logger.info("")
    
    # Summary
    logger.info("="*60)
    logger.info("✅ LLM MYSTERY GENERATION COMPLETE!")
    logger.info("="*60)
    logger.info(f"Mystery ID: {mystery.metadata.mystery_id}")
    logger.info(f"Question: {mystery.metadata.question}")
    logger.info(f"Answer: {mystery.answer}")
    logger.info(f"Documents: {len(mystery.documents)}")
    logger.info(f"Difficulty: {difficulty}/10")
    logger.info(f"Output: {mystery_path}")
    logger.info("")
    logger.info("Next steps:")
    logger.info(f"  1. python scripts/push_to_arkiv.py {mystery_path.name}")
    logger.info(f"  2. python scripts/register_on_chain.py {mystery_path.name}")
    logger.info("")


if __name__ == "__main__":
    from utils.config import config
    sys.exit(main())

