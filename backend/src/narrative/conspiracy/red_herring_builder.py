"""Red Herring Builder - integrates broken evidence chains into documents."""

import logging
import random
from typing import List, Dict, Any
from models.conspiracy import SubGraph, DocumentAssignment


logger = logging.getLogger(__name__)


class RedHerringBuilder:
    """Build and integrate red herring evidence into documents."""
    
    def __init__(self):
        """Initialize builder."""
        pass
    
    def integrate_red_herrings(
        self,
        documents: List[Dict[str, Any]],
        red_herring_subgraphs: List[SubGraph],
        config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Integrate red herring evidence into documents.
        
        Strategy:
        - Mix false evidence naturally into real documents
        - Make it plausible but ultimately unhelpful
        - Some red herrings are obvious dead ends
        - Others are subtle misdirections
        
        Args:
            documents: Generated documents
            red_herring_subgraphs: Broken/false evidence chains
            config: Optional configuration
        
        Returns:
            Documents with red herrings integrated
        """
        config = config or {}
        
        if not red_herring_subgraphs:
            logger.info("⏭️  No red herrings to integrate")
            return documents
        
        logger.info("🎭 Integrating red herrings...")
        logger.info(f"   Red herring chains: {len(red_herring_subgraphs)}")
        
        # Collect red herring evidence
        rh_evidence = []
        for sg in red_herring_subgraphs:
            rh_evidence.extend(sg.evidence_nodes)
        
        if not rh_evidence:
            return documents
        
        logger.info(f"   Red herring evidence nodes: {len(rh_evidence)}")
        
        # Select documents to add red herrings to (20-30%)
        num_to_modify = max(2, int(len(documents) * 0.25))
        target_docs = random.sample(documents, min(num_to_modify, len(documents)))
        
        # Add red herrings
        modified_count = 0
        for doc in target_docs:
            rh_node = random.choice(rh_evidence)
            
            if self._add_red_herring_to_document(doc, rh_node):
                modified_count += 1
        
        logger.info(f"   ✅ Added red herrings to {modified_count} documents")
        logger.info("")
        
        return documents
    
    def _add_red_herring_to_document(
        self,
        document: Dict[str, Any],
        rh_node: Any
    ) -> bool:
        """Add a red herring to a specific document."""
        
        fields = document.get("fields", {})
        
        # Find a text field to add to
        text_fields = [k for k, v in fields.items() if isinstance(v, str)]
        
        if not text_fields:
            return False
        
        # Select field
        target_field = random.choice(text_fields)
        
        # Create red herring text
        rh_text = self._create_red_herring_text(rh_node)
        
        # Add to document
        current_text = fields[target_field]
        fields[target_field] = current_text + "\n\n" + rh_text
        
        document["fields"] = fields
        document["contains_red_herring"] = True
        
        return True
    
    def _create_red_herring_text(self, rh_node: Any) -> str:
        """Create plausible but false text from red herring node."""
        
        # Get content
        content = rh_node.content if hasattr(rh_node, 'content') else str(rh_node)
        
        # Add subtle markers of falseness
        false_markers = [
            "There were also unconfirmed reports of ",
            "Some witnesses claimed ",
            "Initial reports suggested ",
            "Early intelligence indicated "
        ]
        
        marker = random.choice(false_markers)
        
        return f"{marker}{content.lower()}"

