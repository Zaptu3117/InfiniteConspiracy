"""Document-SubGraph Mapper - maps sub-graph nodes to documents."""

import logging
import random
from typing import List, Dict, Any
from models.conspiracy import (
    SubGraph,
    EvidenceNode,
    InferenceNode,
    DocumentAssignment,
    EvidenceType
)


logger = logging.getLogger(__name__)


class DocumentSubGraphMapper:
    """Map sub-graph nodes to documents with constraints."""
    
    def __init__(self):
        """Initialize mapper."""
        self.doc_types = [
            "email", "diary", "internal_memo", "police_report",
            "badge_log", "witness_statement", "surveillance_log",
            "phone_record", "receipt", "bank_statement", "newspaper"
        ]
    
    def map_subgraphs_to_documents(
        self,
        subgraphs: List[SubGraph],
        num_documents: int,
        config: Dict[str, Any] = None
    ) -> List[DocumentAssignment]:
        """
        Map sub-graph nodes to documents.
        
        Strategy:
        - Each document contains evidence from 1-3 nodes
        - Nodes can be from DIFFERENT sub-graphs (cadavre exquis)
        - No single document contains a complete chain
        - Identity nodes: 1 per document (atomic)
        - Psychological nodes: Can combine evidence showing patterns
        - Crypto nodes: Encrypted phrase + separate key hint documents
        
        Args:
            subgraphs: List of sub-graphs
            num_documents: Target number of documents
            config: Optional configuration
        
        Returns:
            List of DocumentAssignment objects
        """
        config = config or {}
        
        logger.info("📄 Mapping sub-graphs to documents...")
        logger.info(f"   Sub-graphs: {len(subgraphs)}")
        logger.info(f"   Target documents: {num_documents}")
        
        # Collect all evidence nodes from all sub-graphs
        all_evidence_nodes = []
        for sg in subgraphs:
            all_evidence_nodes.extend(sg.evidence_nodes)
        
        logger.info(f"   Total evidence nodes: {len(all_evidence_nodes)}")
        
        # Separate by type
        identity_nodes = [n for n in all_evidence_nodes if n.evidence_type == EvidenceType.IDENTITY]
        psychological_nodes = [n for n in all_evidence_nodes if n.evidence_type == EvidenceType.PSYCHOLOGICAL]
        crypto_nodes = [n for n in all_evidence_nodes if n.evidence_type == EvidenceType.CRYPTOGRAPHIC]
        
        logger.info(f"      Identity: {len(identity_nodes)}")
        logger.info(f"      Psychological: {len(psychological_nodes)}")
        logger.info(f"      Cryptographic: {len(crypto_nodes)}")
        
        # Create document assignments
        assignments = []
        assigned_nodes = set()
        
        # Phase 1: Assign identity nodes (1 per document)
        identity_docs = self._assign_identity_nodes(
            identity_nodes,
            assigned_nodes,
            subgraphs
        )
        assignments.extend(identity_docs)
        
        # Phase 2: Assign psychological nodes (can combine)
        psychological_docs = self._assign_psychological_nodes(
            psychological_nodes,
            assigned_nodes,
            subgraphs
        )
        assignments.extend(psychological_docs)
        
        # Phase 3: Assign crypto nodes (encrypted + key hints)
        crypto_docs = self._assign_crypto_nodes(
            crypto_nodes,
            assigned_nodes,
            subgraphs
        )
        assignments.extend(crypto_docs)
        
        # Phase 4: Create connection documents (multi-subgraph)
        connection_docs = self._create_connection_documents(
            subgraphs,
            assigned_nodes,
            num_documents - len(assignments)
        )
        assignments.extend(connection_docs)
        
        # Adjust to target document count
        if len(assignments) < num_documents:
            filler_docs = self._create_filler_documents(
                all_evidence_nodes,
                assigned_nodes,
                num_documents - len(assignments)
            )
            assignments.extend(filler_docs)
        
        logger.info(f"   ✅ Created {len(assignments)} document assignments")
        logger.info(f"      Identity docs: {len(identity_docs)}")
        logger.info(f"      Psychological docs: {len(psychological_docs)}")
        logger.info(f"      Crypto docs: {len(crypto_docs)}")
        logger.info(f"      Connection docs: {len(connection_docs)}")
        logger.info("")
        
        return assignments
    
    def _assign_identity_nodes(
        self,
        nodes: List[EvidenceNode],
        assigned_nodes: set,
        subgraphs: List[SubGraph]
    ) -> List[DocumentAssignment]:
        """Assign identity nodes - 1 per document (atomic)."""
        assignments = []
        
        for node in nodes:
            if node.node_id in assigned_nodes:
                continue
            
            # Identity nodes are atomic - 1 per document
            assignment = DocumentAssignment(
                document_id=f"doc_{len(assignments)}_{node.assigned_doc_type}",
                document_type=node.assigned_doc_type or "server_log",
                evidence_node_ids=[node.node_id],
                inference_node_ids=[],
                subgraph_ids=[node.subgraph_id],
                max_nodes=1,  # ATOMIC
                requires_cross_reference=False,
                contains_encrypted_phrase=False,
                contains_crypto_key=False
            )
            
            assignments.append(assignment)
            assigned_nodes.add(node.node_id)
        
        return assignments
    
    def _assign_psychological_nodes(
        self,
        nodes: List[EvidenceNode],
        assigned_nodes: set,
        subgraphs: List[SubGraph]
    ) -> List[DocumentAssignment]:
        """Assign psychological nodes - can combine 2-3 for patterns."""
        assignments = []
        
        # Group by similar doc types
        by_doc_type = {}
        for node in nodes:
            if node.node_id in assigned_nodes:
                continue
            doc_type = node.assigned_doc_type or "email"
            if doc_type not in by_doc_type:
                by_doc_type[doc_type] = []
            by_doc_type[doc_type].append(node)
        
        # Create documents with 1-2 psychological nodes each
        for doc_type, group_nodes in by_doc_type.items():
            random.shuffle(group_nodes)
            
            for i in range(0, len(group_nodes), 2):
                batch = group_nodes[i:i+2]
                
                assignment = DocumentAssignment(
                    document_id=f"doc_{len(assignments)}_psych_{doc_type}",
                    document_type=doc_type,
                    evidence_node_ids=[n.node_id for n in batch],
                    inference_node_ids=[],
                    subgraph_ids=list(set(n.subgraph_id for n in batch)),
                    max_nodes=2,
                    requires_cross_reference=False,
                    contains_encrypted_phrase=False,
                    contains_crypto_key=False
                )
                
                assignments.append(assignment)
                for node in batch:
                    assigned_nodes.add(node.node_id)
        
        return assignments
    
    def _assign_crypto_nodes(
        self,
        nodes: List[EvidenceNode],
        assigned_nodes: set,
        subgraphs: List[SubGraph]
    ) -> List[DocumentAssignment]:
        """Assign crypto nodes - encrypted phrase + key hints separately."""
        assignments = []
        
        for node in nodes:
            if node.node_id in assigned_nodes:
                continue
            
            # Encrypted phrase document
            if node.encrypted_phrase:
                assignment = DocumentAssignment(
                    document_id=f"doc_{len(assignments)}_encrypted",
                    document_type=node.assigned_doc_type or "email",
                    evidence_node_ids=[node.node_id],
                    inference_node_ids=[],
                    subgraph_ids=[node.subgraph_id],
                    max_nodes=1,
                    requires_cross_reference=True,
                    contains_encrypted_phrase=True,
                    contains_crypto_key=False
                )
                assignments.append(assignment)
                assigned_nodes.add(node.node_id)
            
            # Key hint document (if it's a hint node)
            elif "hint" in node.node_id:
                assignment = DocumentAssignment(
                    document_id=f"doc_{len(assignments)}_key_hint",
                    document_type=node.assigned_doc_type or "diary",
                    evidence_node_ids=[node.node_id],
                    inference_node_ids=[],
                    subgraph_ids=[node.subgraph_id],
                    max_nodes=1,
                    requires_cross_reference=False,
                    contains_encrypted_phrase=False,
                    contains_crypto_key=True
                )
                assignments.append(assignment)
                assigned_nodes.add(node.node_id)
        
        return assignments
    
    def _create_connection_documents(
        self,
        subgraphs: List[SubGraph],
        assigned_nodes: set,
        max_docs: int
    ) -> List[DocumentAssignment]:
        """Create documents that reference multiple sub-graphs."""
        assignments = []
        
        if max_docs <= 0:
            return assignments
        
        # Find nodes from different sub-graphs that can be combined
        available_by_subgraph = {}
        for sg in subgraphs:
            available = [n for n in sg.evidence_nodes if n.node_id not in assigned_nodes]
            if available:
                available_by_subgraph[sg.subgraph_id] = available
        
        # Create connection docs with nodes from 2-3 different sub-graphs
        subgraph_ids = list(available_by_subgraph.keys())
        
        for _ in range(min(max_docs, len(subgraph_ids) // 2)):
            if len(subgraph_ids) < 2:
                break
            
            # Pick 2-3 random sub-graphs
            num_to_combine = random.randint(2, min(3, len(subgraph_ids)))
            selected_sgs = random.sample(subgraph_ids, num_to_combine)
            
            # Pick one node from each
            selected_nodes = []
            for sg_id in selected_sgs:
                nodes = available_by_subgraph.get(sg_id, [])
                if nodes:
                    node = random.choice(nodes)
                    selected_nodes.append(node)
                    assigned_nodes.add(node.node_id)
            
            if len(selected_nodes) >= 2:
                # Choose doc type from first node
                doc_type = selected_nodes[0].assigned_doc_type or random.choice(self.doc_types)
                
                assignment = DocumentAssignment(
                    document_id=f"doc_{len(assignments)}_connection",
                    document_type=doc_type,
                    evidence_node_ids=[n.node_id for n in selected_nodes],
                    inference_node_ids=[],
                    subgraph_ids=selected_sgs,
                    max_nodes=len(selected_nodes),
                    requires_cross_reference=True,
                    contains_encrypted_phrase=False,
                    contains_crypto_key=False
                )
                assignments.append(assignment)
        
        return assignments
    
    def _create_filler_documents(
        self,
        all_nodes: List[EvidenceNode],
        assigned_nodes: set,
        num_needed: int
    ) -> List[DocumentAssignment]:
        """Create filler documents if we need more to reach target."""
        assignments = []
        
        unassigned = [n for n in all_nodes if n.node_id not in assigned_nodes]
        
        if not unassigned:
            return assignments
        
        random.shuffle(unassigned)
        
        for i in range(min(num_needed, len(unassigned))):
            node = unassigned[i]
            
            assignment = DocumentAssignment(
                document_id=f"doc_{1000 + len(assignments)}_filler",
                document_type=node.assigned_doc_type or random.choice(self.doc_types),
                evidence_node_ids=[node.node_id],
                inference_node_ids=[],
                subgraph_ids=[node.subgraph_id],
                max_nodes=1,
                requires_cross_reference=False,
                contains_encrypted_phrase=False,
                contains_crypto_key=False
            )
            assignments.append(assignment)
            assigned_nodes.add(node.node_id)
        
        return assignments

