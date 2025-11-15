"""Image Clue Mapper - maps sub-graph nodes to visual evidence."""

import logging
import random
from typing import List, Dict, Any
from models.conspiracy import (
    SubGraph,
    EvidenceNode,
    ImageClue,
    EvidenceType
)


logger = logging.getLogger(__name__)


class ImageClueMapper:
    """Map sub-graph evidence to visual clues in images."""
    
    def __init__(self):
        """Initialize mapper."""
        self.image_types = ["photograph", "document", "symbol", "object"]
    
    def map_evidence_to_images(
        self,
        subgraphs: List[SubGraph],
        num_images: int = 5
    ) -> List[ImageClue]:
        """
        Map evidence nodes to visual clues.
        
        Args:
            subgraphs: Sub-graphs with evidence
            num_images: Target number of images
        
        Returns:
            List of ImageClue objects
        """
        logger.info("🖼️  Mapping evidence to image clues...")
        logger.info(f"   Target images: {num_images}")
        
        # Select interesting evidence nodes for images
        selected_nodes = self._select_nodes_for_images(subgraphs, num_images)
        
        # Create image clues
        image_clues = []
        for i, node in enumerate(selected_nodes):
            image_clue = self._create_image_clue(f"img_{i}", node)
            image_clues.append(image_clue)
        
        logger.info(f"   ✅ Created {len(image_clues)} image clues")
        for ic in image_clues:
            logger.info(f"      - {ic.image_id}: {ic.image_type} ({len(ic.visual_clues)} clues)")
        logger.info("")
        
        return image_clues
    
    def _select_nodes_for_images(
        self,
        subgraphs: List[SubGraph],
        num_images: int
    ) -> List[EvidenceNode]:
        """Select evidence nodes that work well as images."""
        
        candidates = []
        
        for sg in subgraphs:
            if sg.is_red_herring:
                continue  # Skip red herring images for now
            
            for node in sg.evidence_nodes:
                # Identity nodes: Good for surveillance, badges
                if node.evidence_type == EvidenceType.IDENTITY:
                    if any(term in node.content.lower() for term in ["badge", "access", "photo", "camera"]):
                        candidates.append(node)
                
                # Psychological: Good for personal items, symbolic objects
                elif node.evidence_type == EvidenceType.PSYCHOLOGICAL:
                    candidates.append(node)
                
                # Crypto: Good for symbols, coded imagery
                elif node.evidence_type == EvidenceType.CRYPTOGRAPHIC:
                    candidates.append(node)
        
        # Select random subset
        selected = random.sample(candidates, min(num_images, len(candidates)))
        
        return selected
    
    def _create_image_clue(
        self,
        image_id: str,
        evidence_node: EvidenceNode
    ) -> ImageClue:
        """Create an image clue from evidence node."""
        
        # Determine image type based on evidence
        if evidence_node.evidence_type == EvidenceType.IDENTITY:
            image_type = random.choice(["photograph", "document"])
            visual_clues = self._extract_identity_clues(evidence_node)
        
        elif evidence_node.evidence_type == EvidenceType.PSYCHOLOGICAL:
            image_type = random.choice(["photograph", "object"])
            visual_clues = self._extract_psychological_clues(evidence_node)
        
        elif evidence_node.evidence_type == EvidenceType.CRYPTOGRAPHIC:
            image_type = random.choice(["symbol", "document"])
            visual_clues = self._extract_crypto_clues(evidence_node)
        
        else:
            image_type = "photograph"
            visual_clues = [evidence_node.content[:100]]
        
        # Generate description and prompt
        description = self._generate_image_description(evidence_node, image_type)
        prompt = self._generate_image_prompt(evidence_node, image_type, visual_clues)
        
        return ImageClue(
            image_id=image_id,
            image_type=image_type,
            description=description,
            visual_clues=visual_clues,
            evidence_node_ids=[evidence_node.node_id],
            subgraph_id=evidence_node.subgraph_id,
            prompt=prompt
        )
    
    def _extract_identity_clues(self, node: EvidenceNode) -> List[str]:
        """Extract visual clues from identity evidence."""
        clues = []
        
        if node.identifier_type == "badge_number":
            clues.append(f"Badge number visible: {node.identifier_value}")
        elif node.identifier_type == "ip_address":
            clues.append(f"IP address in log: {node.identifier_value}")
        elif "device" in node.identifier_type:
            clues.append(f"Device ID label: {node.identifier_value}")
        else:
            clues.append(node.content[:100])
        
        return clues
    
    def _extract_psychological_clues(self, node: EvidenceNode) -> List[str]:
        """Extract visual clues from psychological evidence."""
        return [
            "Body language showing stress",
            "Personal items revealing character",
            node.content[:80]
        ]
    
    def _extract_crypto_clues(self, node: EvidenceNode) -> List[str]:
        """Extract visual clues from crypto evidence."""
        clues = []
        
        if node.encrypted_phrase:
            clues.append(f"Encrypted text visible: {node.encrypted_phrase[:50]}")
        if node.key_hint:
            clues.append("Symbolic imagery suggesting key")
        
        return clues
    
    def _generate_image_description(
        self,
        node: EvidenceNode,
        image_type: str
    ) -> str:
        """Generate description of what image shows."""
        
        descriptions = {
            "photograph": f"Surveillance photograph showing: {node.content[:80]}",
            "document": f"Document image containing: {node.content[:80]}",
            "symbol": f"Symbolic imagery related to: {node.content[:80]}",
            "object": f"Physical object photographed: {node.content[:80]}"
        }
        
        return descriptions.get(image_type, node.content[:100])
    
    def _generate_image_prompt(
        self,
        node: EvidenceNode,
        image_type: str,
        visual_clues: List[str]
    ) -> str:
        """Generate image generation prompt."""
        
        prompts = {
            "photograph": f"Surveillance photograph, security camera view, showing {', '.join(visual_clues[:2])}, professional, high quality",
            "document": f"Close-up of document with visible text and details, {', '.join(visual_clues[:2])}, photorealistic",
            "symbol": f"Occult symbol or coded imagery, mysterious, {', '.join(visual_clues[:1])}, dark atmosphere",
            "object": f"Physical evidence photograph, forensic style, {', '.join(visual_clues[:2])}, detailed"
        }
        
        return prompts.get(image_type, f"Image showing {node.content[:50]}")

