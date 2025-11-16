"""Psychological Node Generator - LLM-generated behavioral and motive evidence."""

import logging
from typing import List, Dict, Any
from models.conspiracy import (
    EvidenceNode,
    InferenceNode,
    EvidenceType,
    AnswerDimension,
    ConspiracyPremise,
    PoliticalContext,
    MysteryAnswer
)


logger = logging.getLogger(__name__)


PSYCHOLOGICAL_EVIDENCE_PROMPT = """You are creating psychological/behavioral evidence for a conspiracy mystery.

CONSPIRACY CONTEXT:
{conspiracy_context}

OPERATION NAME: {operation_name}

POLITICAL CONTEXT:
{political_context_summary}

TARGET WHY PHRASE (MUST EMBED): "{why_phrase}"

YOUR TASK:
Generate {num_nodes} pieces of psychological evidence that reveal behavioral patterns, stress indicators, relationship dynamics, or motive clues.

OPERATION NAME REFERENCES:
- When characters mention the operation, use INDIRECT references:
  * "the operation" / "the mission" / "our work" / "the project"
  * "what we're doing" / "the plan" / "the task"
  * Internal nicknames or partial names
- AVOID using the full operation codename "{operation_name}" in psychological evidence
- The operation name is classified; characters wouldn't casually mention it

CRITICAL REQUIREMENT - EMBED THE WHY PHRASE:
The exact phrase "{why_phrase}" MUST appear verbatim in AT LEAST 2 of the evidence pieces.

Ways to naturally embed the phrase:
1. Character quotes it in an email or communication
2. Appears in a diary entry or personal reflection
3. Witness reports hearing the character say it
4. Found in an internal memo or manifesto
5. Part of a ritual phrase or motto repeated by conspirators

Examples:
- Email: "Dr. X wrote: 'Remember, {why_phrase}. That is our mission.'"
- Diary: "Today I committed to the cause. {why_phrase} - this drives everything."
- Witness: "I overheard them saying '{why_phrase}' during the meeting."
- Memo: "Subject: Mission Statement - {why_phrase}"

TYPES OF PSYCHOLOGICAL EVIDENCE:
1. Stress Indicators: Email tone changes, anxiety in communications, behavior shifts
2. Relationship Dynamics: Trust erosion, manipulation patterns, secret alliances
3. Motive Clues: Financial pressure, ideological alignment, coercion signs, revenge indicators
4. Behavior Patterns: Unusual schedules, secret meetings, paranoid actions
5. Communication Patterns: Coded language, emotional intensity, deception signs

IMPORTANT:
- Each piece should be SUBTLE - not obvious conclusions
- Spread evidence across different people/situations
- Requires reading MULTIPLE pieces to see the pattern
- Should feel like real human behavior, not contrived clues
- AT LEAST 2 pieces MUST contain the exact phrase "{why_phrase}"

Output JSON array with {num_nodes} evidence objects:
[
  {{
    "content": "Specific behavioral observation or pattern (INCLUDE '{why_phrase}' in at least 2 pieces)",
    "psychological_indicator": "stress|paranoia|deception|manipulation|coercion|ideology",
    "importance": "key|supporting|minor",
    "doc_type": "email|diary|witness_statement|internal_memo|phone_record"
  }}
]"""


PSYCHOLOGICAL_INFERENCE_PROMPT = """You are creating psychological inferences for a conspiracy mystery.

EVIDENCE COLLECTED:
{evidence_summary}

CONSPIRACY CONTEXT:
{conspiracy_context}

TARGET WHY PHRASE: "{why_phrase}"

YOUR TASK:
Generate {num_inferences} inference statements that connect the psychological evidence.

These inferences should:
- Connect behavioral patterns across evidence
- Reveal relationships between conspirators
- Suggest motives without stating them outright
- Show progression of events/psychology
- Lead toward understanding why the phrase "{why_phrase}" is significant
- Connect evidence that contains the WHY phrase to other behavioral patterns

The goal is to help players understand that "{why_phrase}" represents the core motivation.

Output JSON array:
[
  {{
    "inference": "What can be concluded from connecting the evidence",
    "reasoning_type": "pattern_recognition|relationship_analysis|motive_inference|behavioral_synthesis"
  }}
]"""


class PsychologicalNodeGenerator:
    """Generate psychological evidence nodes using LLM."""
    
    def __init__(self, llm_client):
        """
        Initialize generator.
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
    
    async def generate_psychological_chain(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        architecture: Any,
        answer_template: MysteryAnswer,
        config: Dict[str, Any] = None
    ) -> tuple[List[EvidenceNode], List[InferenceNode]]:
        """
        Generate psychological chain nodes.
        
        Args:
            subgraph_id: Sub-graph identifier
            premise: Conspiracy premise
            political_context: Political backdrop
            architecture: Sub-graph architecture
            answer_template: Answer template with discoverable WHY phrase
            config: Optional configuration
        
        Returns:
            Tuple of (evidence_nodes, inference_nodes)
        """
        config = config or {}
        
        # Count evidence nodes in architecture
        num_evidence = sum(1 for node in architecture.nodes if node.node_type == "evidence")
        num_inference = sum(1 for node in architecture.nodes if node.node_type == "inference")
        
        logger.info(f"   Generating psychological chain {subgraph_id}...")
        logger.info(f"      Evidence nodes: {num_evidence}, Inferences: {num_inference}")
        logger.info(f"      Target WHY phrase: \"{answer_template.why}\"")
        
        # Generate evidence nodes
        evidence_nodes = await self._generate_evidence_nodes(
            subgraph_id,
            premise,
            political_context,
            answer_template,
            num_evidence,
            config
        )
        
        # Generate inference nodes
        inference_nodes = await self._generate_inference_nodes(
            subgraph_id,
            premise,
            answer_template,
            evidence_nodes,
            num_inference,
            config
        )
        
        return evidence_nodes, inference_nodes
    
    async def _generate_evidence_nodes(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        political_context: PoliticalContext,
        answer_template: MysteryAnswer,
        num_nodes: int,
        config: Dict[str, Any]
    ) -> List[EvidenceNode]:
        """Generate psychological evidence nodes with embedded WHY phrase."""
        
        # Build context
        conspiracy_context = f"""
WHO: {premise.who[:300]}...
WHAT: {premise.what[:300]}...
WHY: {premise.why[:300]}...
HOW: {premise.how[:200]}...
"""
        
        political_summary = f"""
World: {political_context.world_name}
Hidden Reality: {political_context.hidden_reality}
Key Tensions: {', '.join(political_context.unresolved_tensions[:2])}
"""
        
        # Build prompt with WHY phrase to embed
        prompt = PSYCHOLOGICAL_EVIDENCE_PROMPT.format(
            conspiracy_context=conspiracy_context,
            operation_name=answer_template.what,
            political_context_summary=political_summary,
            why_phrase=answer_template.why,
            num_nodes=num_nodes
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 3000)  # High limit to prevent truncation
            )
            
            # Parse response
            if isinstance(response, list):
                evidence_data = response
            else:
                evidence_data = response.get("evidence", [])
            
            # Create EvidenceNode objects
            evidence_nodes = []
            for i, data in enumerate(evidence_data[:num_nodes]):
                node = EvidenceNode(
                    node_id=f"{subgraph_id}_psych_ev_{i}",
                    evidence_type=EvidenceType.PSYCHOLOGICAL,
                    content=data.get("content", "Behavioral observation"),
                    psychological_indicator=data.get("psychological_indicator", "stress"),
                    assigned_doc_type=data.get("doc_type", "email"),
                    isolated=True,
                    importance=data.get("importance", "supporting"),
                    subgraph_id=subgraph_id
                )
                evidence_nodes.append(node)
            
            return evidence_nodes
        
        except Exception as e:
            logger.error(f"   ❌ Psychological evidence generation failed: {e}")
            # Return fallback nodes
            return self._create_fallback_evidence(subgraph_id, num_nodes, premise)
    
    async def _generate_inference_nodes(
        self,
        subgraph_id: str,
        premise: ConspiracyPremise,
        answer_template: MysteryAnswer,
        evidence_nodes: List[EvidenceNode],
        num_inferences: int,
        config: Dict[str, Any]
    ) -> List[InferenceNode]:
        """Generate psychological inference nodes that connect to WHY phrase."""
        
        # Summarize evidence
        evidence_summary = "\n".join([
            f"- {node.content}"
            for node in evidence_nodes
        ])
        
        conspiracy_context = f"""
WHY PHRASE: {answer_template.why}
WHO (Primary): {answer_template.who}
WHAT (Operation): {answer_template.what}
"""
        
        # Build prompt
        prompt = PSYCHOLOGICAL_INFERENCE_PROMPT.format(
            evidence_summary=evidence_summary,
            conspiracy_context=conspiracy_context,
            num_inferences=num_inferences,
            why_phrase=answer_template.why
        )
        
        try:
            # Generate with LLM
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.6),
                max_tokens=config.get("max_tokens", 3000)  # High limit to prevent truncation
            )
            
            # Parse response
            if isinstance(response, list):
                inference_data = response
            else:
                inference_data = response.get("inferences", [])
            
            # Create InferenceNode objects
            inference_nodes = []
            for i, data in enumerate(inference_data[:num_inferences]):
                # Determine parent nodes (previous evidence)
                parent_ids = [node.node_id for node in evidence_nodes[:i+2]]
                
                node = InferenceNode(
                    node_id=f"{subgraph_id}_psych_inf_{i}",
                    inference=data.get("inference", "Pattern detected in behavior"),
                    reasoning_type=data.get("reasoning_type", "pattern_recognition"),
                    parent_node_ids=parent_ids,
                    required_document_ids=[],
                    contributes_to=AnswerDimension.WHY,
                    subgraph_id=subgraph_id
                )
                inference_nodes.append(node)
            
            return inference_nodes
        
        except Exception as e:
            logger.error(f"   ❌ Psychological inference generation failed: {e}")
            return self._create_fallback_inferences(subgraph_id, evidence_nodes, num_inferences)
    
    def _create_fallback_evidence(
        self,
        subgraph_id: str,
        num_nodes: int,
        premise: ConspiracyPremise
    ) -> List[EvidenceNode]:
        """Create fallback psychological evidence."""
        fallback_evidence = [
            ("Email tone shows increasing stress and paranoia", "stress", "email"),
            ("Unusual meeting schedule with suspicious contacts", "deception", "witness_statement"),
            ("Private diary reveals ideological commitment", "ideology", "diary"),
            ("Communication patterns suggest coordination", "manipulation", "phone_record"),
            ("Behavior changes after key political events", "paranoia", "internal_memo")
        ]
        
        nodes = []
        for i in range(min(num_nodes, len(fallback_evidence))):
            content, indicator, doc_type = fallback_evidence[i]
            node = EvidenceNode(
                node_id=f"{subgraph_id}_psych_ev_{i}",
                evidence_type=EvidenceType.PSYCHOLOGICAL,
                content=content,
                psychological_indicator=indicator,
                assigned_doc_type=doc_type,
                isolated=True,
                importance="supporting",
                subgraph_id=subgraph_id
            )
            nodes.append(node)
        
        return nodes
    
    def _create_fallback_inferences(
        self,
        subgraph_id: str,
        evidence_nodes: List[EvidenceNode],
        num_inferences: int
    ) -> List[InferenceNode]:
        """Create fallback psychological inferences."""
        fallback_inferences = [
            "Behavioral pattern indicates growing psychological pressure",
            "Communication analysis reveals coordinated deception",
            "Relationship dynamics suggest manipulation and control",
            "Motive becomes clear through pattern of actions"
        ]
        
        nodes = []
        for i in range(min(num_inferences, len(fallback_inferences))):
            parent_ids = [node.node_id for node in evidence_nodes[:i+2]]
            
            node = InferenceNode(
                node_id=f"{subgraph_id}_psych_inf_{i}",
                inference=fallback_inferences[i],
                reasoning_type="pattern_recognition",
                parent_node_ids=parent_ids,
                required_document_ids=[],
                contributes_to=AnswerDimension.WHY,
                subgraph_id=subgraph_id
            )
            nodes.append(node)
        
        return nodes

