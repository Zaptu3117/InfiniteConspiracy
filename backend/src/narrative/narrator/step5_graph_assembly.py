"""Step 5: Graph Assembly - create document references."""

import logging
from typing import List, Dict, Any
from narrative.graph import Character, TimelineEvent, DocumentPlan, Reference


logger = logging.getLogger(__name__)


GRAPH_ASSEMBLY_PROMPT = """You are creating the document reference graph for a mystery.

DOCUMENT PLAN:
{document_plan_summary}

CONTEXT:
Characters: {num_characters}
Timeline: {time_range}
Question: {question}

YOUR TASK:
For each document, determine which OTHER documents it should reference.

References create the investigation path - they guide players between documents.

For each document, create 0-3 references to other documents:
- doc_id: The source document  
- references: Array of references to other documents

Each reference must have:
- target_doc_id: The document being referenced
- reference_type: One of:
  * "explicit" - directly mentions the other document (e.g., "see attached memo")
  * "implicit" - hints at connection without naming (e.g., "the meeting yesterday")
  * "temporal" - time-based connection (e.g., same timestamp range)
- context: HOW/WHY the reference makes narrative sense (1 sentence)

RULES:
- Not every document needs references
- Create a web of connections, not a linear chain
- References should feel natural, not forced
- Some clusters of related documents, some standalone
- References help reveal the investigation path

Output ONLY valid JSON:
{{
  "document_graph": [
    {{
      "doc_id": "doc_1_email",
      "references": [
        {{
          "target_doc_id": "doc_5_badge_log",
          "reference_type": "explicit",
          "context": "Email mentions checking badge logs for that night"
        }},
        {{
          "target_doc_id": "doc_3_memo",
          "reference_type": "implicit",
          "context": "Refers to 'classified memo' without naming it"
        }}
      ]
    }}
  ]
}}"""


class GraphAssembler:
    """Assemble document reference graph using LLM."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def assemble_graph(
        self,
        document_plan: List[DocumentPlan],
        characters: List[Character],
        timeline: List[TimelineEvent],
        mystery_context: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[DocumentPlan]:
        """
        Create reference edges between documents.
        
        Args:
            document_plan: Document plans from Step 4
            characters: Characters from Step 1
            timeline: Timeline from Step 2
            mystery_context: Mystery details
            config: Configuration
        
        Returns:
            Updated document plans with references
        """
        logger.info("🕸️  Step 5: Assembling document graph...")
        
        # Build prompt
        prompt = self._build_prompt(
            document_plan,
            characters,
            timeline,
            mystery_context
        )
        
        # Generate with LLM
        try:
            response = await self.llm.generate_json(
                prompt,
                temperature=config.get("temperature", 0.5),
                max_tokens=config.get("max_tokens", 2500)
            )
            
            # Parse references and update document plans
            doc_graph = response.get("document_graph", [])
            doc_map = {doc.doc_id: doc for doc in document_plan}
            
            for doc_refs in doc_graph:
                doc_id = doc_refs.get("doc_id")
                if doc_id in doc_map:
                    references = [
                        Reference.from_dict(ref)
                        for ref in doc_refs.get("references", [])
                    ]
                    doc_map[doc_id].references = references
            
            # Calculate statistics
            total_refs = sum(len(doc.references) for doc in document_plan)
            avg_refs = total_refs / len(document_plan) if document_plan else 0
            
            logger.info(f"   ✅ Graph assembled")
            logger.info(f"      - {total_refs} total references")
            logger.info(f"      - {avg_refs:.1f} references per document (avg)")
            
            # Show reference types
            ref_types = {}
            for doc in document_plan:
                for ref in doc.references:
                    ref_types[ref.reference_type] = ref_types.get(ref.reference_type, 0) + 1
            
            for ref_type, count in sorted(ref_types.items()):
                logger.info(f"      - {count}x {ref_type} references")
            
            return document_plan
        
        except Exception as e:
            logger.error(f"   ❌ Graph assembly failed: {e}")
            raise
    
    def _build_prompt(
        self,
        document_plan: List[DocumentPlan],
        characters: List[Character],
        timeline: List[TimelineEvent],
        mystery_context: Dict[str, Any]
    ) -> str:
        """Build the graph assembly prompt."""
        
        # Summarize document plan
        doc_summary = self._summarize_document_plan(document_plan)
        
        # Calculate time range
        if timeline:
            first_time = timeline[0].timestamp[:10]
            last_time = timeline[-1].timestamp[:10]
            time_range = f"{first_time} to {last_time}"
        else:
            time_range = "Multiple days"
        
        # Fill prompt template
        prompt = GRAPH_ASSEMBLY_PROMPT.format(
            document_plan_summary=doc_summary,
            num_characters=len(characters),
            time_range=time_range,
            question=mystery_context.get("question", "")
        )
        
        return prompt
    
    def _summarize_document_plan(self, document_plan: List[DocumentPlan]) -> str:
        """Summarize document plan for prompt."""
        lines = []
        for doc in document_plan:
            clue_count = len(doc.clues_to_include)
            red_herring = " (RED HERRING)" if doc.is_red_herring else ""
            lines.append(
                f"- {doc.doc_id}: {doc.doc_type} by {doc.author} "
                f"at {doc.timestamp[:16]} ({clue_count} clues){red_herring}"
            )
        return "\n".join(lines)

