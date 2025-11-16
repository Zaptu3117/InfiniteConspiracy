"""
Evidence Fact Extractor

Extracts atomic facts from evidence nodes using LLM for semantic understanding.
"""

from typing import List, Optional
from dataclasses import dataclass
from models.conspiracy import EvidenceNode, SubGraph, MysteryAnswer
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class AtomicFact:
    """
    Represents one atomic piece of information that can appear in a document.
    """
    fact_id: str
    fact_type: str  # "name", "badge_number", "ip_address", "operation_codename", etc.
    value: str
    source_node_id: str
    source_chain: str  # e.g., "identity_chain_1", "crypto_chain_2"
    is_answer_critical: bool = False
    answer_dimension: Optional[str] = None  # "who", "what", "why", "how"
    
    def __repr__(self):
        critical = f" [ANSWER:{self.answer_dimension}]" if self.is_answer_critical else ""
        return f"<Fact {self.fact_type}={self.value} from {self.source_chain}{critical}>"


class EvidenceFactExtractor:
    """
    Extracts atomic facts from evidence chains using LLM for semantic understanding.
    """
    
    def __init__(self, llm_client):
        """Initialize with LLM client for fact extraction."""
        self.llm = llm_client
    
    async def extract_all_facts(
        self,
        subgraphs: List[SubGraph],
        answer_template: MysteryAnswer
    ) -> List[AtomicFact]:
        """
        Extract all atomic facts from all evidence chains.
        
        Args:
            subgraphs: List of evidence subgraphs
            answer_template: The correct answers (to mark answer-critical facts)
        
        Returns:
            List of atomic facts with answer-critical markers
        """
        all_facts = []
        fact_counter = 0
        
        for subgraph in subgraphs:
            chain_id = subgraph.subgraph_id
            chain_type = subgraph.subgraph_type.value
            
            logger.info(f"Extracting facts from {chain_id} ({chain_type})")
            
            for evidence_node in subgraph.evidence_nodes:
                facts = await self._extract_facts_from_node_with_llm(
                    evidence_node,
                    chain_id,
                    chain_type,
                    answer_template,
                    fact_counter
                )
                all_facts.extend(facts)
                fact_counter += len(facts)
        
        logger.info(f"Extracted {len(all_facts)} total atomic facts")
        answer_critical = [f for f in all_facts if f.is_answer_critical]
        logger.info(f"  - {len(answer_critical)} answer-critical facts")
        
        return all_facts
    
    async def _extract_facts_from_node_with_llm(
        self,
        node: EvidenceNode,
        chain_id: str,
        chain_type: str,
        answer_template: MysteryAnswer,
        fact_counter: int
    ) -> List[AtomicFact]:
        """
        Extract atomic facts from an evidence node using LLM.
        
        The LLM identifies concrete, atomic pieces of information that should
        appear in documents.
        """
        
        prompt = f"""Extract atomic facts from this evidence node.

EVIDENCE TYPE: {chain_type}
EVIDENCE CONTENT:
{node.content}

ANSWER CONTEXT (to mark answer-critical facts):
- WHO answer: {answer_template.who}
- WHAT answer: {answer_template.what}
- WHY answer: {answer_template.why}
- HOW answer: {answer_template.how}

INSTRUCTIONS:
Extract ATOMIC facts - small, concrete pieces of information that can appear in documents.

For IDENTITY evidence, extract:
- Badge numbers (e.g., "badge_number: 5778")
- IP addresses (e.g., "ip_address: 10.2.3.4")
- User IDs (e.g., "user_id: jdoe_2024")
- MAC addresses
- Employee IDs
- Person names (e.g., "name: Dr. Jane Doe")

For PSYCHOLOGICAL evidence, extract:
- Key motivation phrases that appear verbatim
- Character behavioral traits (short descriptions, 1-2 sentences max)
- NOT long text blocks - only concrete observations

For CRYPTOGRAPHIC evidence, extract:
- Operation codenames
- Method descriptions (tactics/techniques)
- Encrypted message fragments (short, concrete pieces)
- NOT entire message transcripts - only key phrases

CRITICAL RULES:
1. Each fact should be SHORT (typically 3-10 words, max 20 words)
2. Facts should be CONCRETE and SPECIFIC
3. Mark facts as answer-critical ONLY if they contain the exact answer text
4. For identity: extract ALL technical identifiers separately
5. For psychological/crypto: extract KEY PHRASES only, not full narratives

OUTPUT FORMAT (JSON array):
[
  {{
    "fact_type": "badge_number",
    "value": "5778",
    "is_answer_critical": false,
    "answer_dimension": null
  }},
  {{
    "fact_type": "name",
    "value": "Dr. Jane Doe",
    "is_answer_critical": true,
    "answer_dimension": "who"
  }},
  {{
    "fact_type": "motivation_phrase",
    "value": "cement national security",
    "is_answer_critical": true,
    "answer_dimension": "why"
  }}
]

Extract 2-5 atomic facts. Focus on QUALITY over quantity."""

        try:
            response = await self.llm.generate_json(prompt, temperature=0.3, max_tokens=1000)
            
            # Convert to AtomicFact objects
            facts = []
            if isinstance(response, list):
                for i, fact_data in enumerate(response):
                    fact = AtomicFact(
                        fact_id=f"fact_{fact_counter + i}",
                        fact_type=fact_data.get("fact_type", "unknown"),
                        value=fact_data.get("value", ""),
                        source_node_id=node.node_id,
                        source_chain=chain_id,
                        is_answer_critical=fact_data.get("is_answer_critical", False),
                        answer_dimension=fact_data.get("answer_dimension")
                    )
                    facts.append(fact)
                    logger.debug(f"    Extracted: {fact}")
            
            return facts
            
        except Exception as e:
            logger.warning(f"    LLM fact extraction failed for {node.node_id}: {e}")
            logger.warning(f"    Falling back to simple extraction")
            return self._fallback_extract_facts(node, chain_id, chain_type, answer_template, fact_counter)
    
    def _fallback_extract_facts(
        self,
        node: EvidenceNode,
        chain_id: str,
        chain_type: str,
        answer_template: MysteryAnswer,
        fact_counter: int
    ) -> List[AtomicFact]:
        """
        Simple fallback extraction if LLM fails.
        Extracts basic identifiers only.
        """
        facts = []
        
        # Extract identifier if present (for identity nodes)
        if node.identifier_type and node.identifier_value:
            is_who_answer = (
                node.identifier_type == "name" and 
                answer_template.who and
                node.identifier_value.lower() == answer_template.who.lower()
            )
            
            fact = AtomicFact(
                fact_id=f"fact_{fact_counter}",
                fact_type=node.identifier_type,
                value=node.identifier_value,
                source_node_id=node.node_id,
                source_chain=chain_id,
                is_answer_critical=is_who_answer,
                answer_dimension="who" if is_who_answer else None
            )
            facts.append(fact)
        
        # Extract answer phrases if present in content
        if node.content:
            if answer_template.what and answer_template.what.lower() in node.content.lower():
                facts.append(AtomicFact(
                    fact_id=f"fact_{fact_counter + len(facts)}",
                    fact_type="operation_codename",
                    value=answer_template.what,
                    source_node_id=node.node_id,
                    source_chain=chain_id,
                    is_answer_critical=True,
                    answer_dimension="what"
                ))
            
            if answer_template.why and answer_template.why.lower() in node.content.lower():
                facts.append(AtomicFact(
                    fact_id=f"fact_{fact_counter + len(facts)}",
                    fact_type="motivation_phrase",
                    value=answer_template.why,
                    source_node_id=node.node_id,
                    source_chain=chain_id,
                    is_answer_critical=True,
                    answer_dimension="why"
                ))
            
            if answer_template.how and answer_template.how.lower() in node.content.lower():
                facts.append(AtomicFact(
                    fact_id=f"fact_{fact_counter + len(facts)}",
                    fact_type="method_description",
                    value=answer_template.how,
                    source_node_id=node.node_id,
                    source_chain=chain_id,
                    is_answer_critical=True,
                    answer_dimension="how"
                ))
        
        return facts

