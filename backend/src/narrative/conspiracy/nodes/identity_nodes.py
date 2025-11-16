"""Identity Node Generator - programmatic generation of technical identifier chains."""

import logging
import random
import time
from typing import List, Dict, Any, Optional
from models.conspiracy import EvidenceNode, InferenceNode, EvidenceType


logger = logging.getLogger(__name__)


class IdentityNodeGenerator:
    """Generate identity chain nodes programmatically."""
    
    def __init__(self):
        """Initialize generator."""
        self.identifier_types = {
            "network": ["ip_address", "mac_address", "vpn_session", "connection_id"],
            "auth": ["user_id", "username", "employee_number", "badge_number"],
            "physical": ["badge_scan", "fingerprint_id", "keycard"],
            "system": ["device_id", "workstation_name", "asset_tag"],
            "transaction": ["transaction_id", "request_id", "ticket_id", "case_number"]
        }
        
        self.doc_types = {
            "network": ["server_log", "network_log", "firewall_log", "vpn_log"],
            "auth": ["auth_log", "login_history", "access_control"],
            "physical": ["badge_log", "door_access_log", "security_scan"],
            "system": ["asset_database", "it_inventory", "device_registry"],
            "transaction": ["audit_log", "transaction_history", "system_log"],
            "mapping": ["hr_directory", "employee_database", "user_registry"]
        }
    
    def generate_identity_chain(
        self,
        subgraph_id: str,
        target_character: Dict[str, Any],
        difficulty: int,
        architecture: Any
    ) -> tuple[List[EvidenceNode], List[InferenceNode]]:
        """
        Generate identity chain nodes.
        
        Args:
            subgraph_id: Sub-graph identifier
            target_character: Character dict with name, role, involvement_level, etc.
            difficulty: Complexity level
            architecture: Sub-graph architecture spec
        
        Returns:
            Tuple of (evidence_nodes, inference_nodes)
        """
        evidence_nodes = []
        inference_nodes = []
        
        # Extract target name from character
        target_name = target_character.get("name", "Unknown")
        
        # Generate unique identifiers for this chain
        identifiers = self._generate_identifiers(target_name, architecture)
        
        # Build evidence nodes
        node_idx = 0
        for node_spec in architecture.nodes:
            if node_spec.node_type == "evidence":
                evidence_node = self._create_evidence_node(
                    f"{subgraph_id}_ev_{node_idx}",
                    subgraph_id,
                    node_spec,
                    identifiers,
                    node_idx
                )
                evidence_nodes.append(evidence_node)
                node_idx += 1
            
            elif node_spec.node_type == "inference":
                inference_node = self._create_inference_node(
                    f"{subgraph_id}_inf_{node_idx}",
                    subgraph_id,
                    node_spec,
                    evidence_nodes,
                    inference_nodes,
                    target_name
                )
                inference_nodes.append(inference_node)
                node_idx += 1
        
        return evidence_nodes, inference_nodes
    
    def _generate_identifiers(
        self,
        target_name: str,
        architecture: Any
    ) -> Dict[str, str]:
        """Generate unique identifiers for this chain."""
        identifiers = {}
        
        # Generate based on name but with randomness
        name_hash = hash(target_name + str(time.time()))
        
        # IP address
        identifiers["ip_address"] = self._generate_ip()
        
        # MAC address
        identifiers["mac_address"] = self._generate_mac()
        
        # Session/Connection IDs
        identifiers["vpn_session"] = self._generate_session_id("VPN")
        identifiers["connection_id"] = self._generate_session_id("CONN")
        identifiers["request_id"] = self._generate_session_id("REQ")
        
        # User identifiers
        identifiers["user_id"] = self._generate_user_id(target_name)
        identifiers["username"] = identifiers["user_id"]
        
        # Badge and physical
        identifiers["badge_number"] = str(random.randint(1000, 9999))
        identifiers["badge_scan"] = identifiers["badge_number"]
        identifiers["keycard"] = str(random.randint(5000, 8999))
        identifiers["fingerprint_id"] = f"FP{random.randint(10000, 99999)}"
        
        # Employee ID
        identifiers["employee_number"] = str(abs(name_hash) % 9000 + 1000)
        
        # Device
        identifiers["device_id"] = f"WS-{random.randint(1000, 9999)}"
        identifiers["workstation_name"] = f"DESKTOP-{random.randint(100, 999)}"
        identifiers["asset_tag"] = f"AST{random.randint(10000, 99999)}"
        
        # Transaction
        identifiers["transaction_id"] = f"TXN-{random.randint(100000, 999999)}"
        identifiers["ticket_id"] = f"TKT-{random.randint(10000, 99999)}"
        identifiers["case_number"] = f"CASE-{random.randint(1000, 9999)}"
        
        # Name
        identifiers["name"] = target_name
        
        return identifiers
    
    def _generate_ip(self) -> str:
        """Generate random IP address."""
        return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def _generate_mac(self) -> str:
        """Generate random MAC address."""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def _generate_session_id(self, prefix: str) -> str:
        """Generate session/connection ID."""
        suffix = ''.join(random.choices('ABCDEF0123456789', k=8))
        return f"{prefix}_{suffix}"
    
    def _generate_user_id(self, name: str) -> str:
        """Generate user ID from name."""
        parts = name.lower().split()
        if len(parts) >= 2:
            formats = [
                f"{parts[0][0]}{parts[-1]}",  # jdoe
                f"{parts[0]}.{parts[-1]}",     # john.doe
                f"{parts[0]}{parts[-1][0]}",   # johnd
            ]
            return random.choice(formats)
        return parts[0] if parts else "user"
    
    def _create_evidence_node(
        self,
        node_id: str,
        subgraph_id: str,
        node_spec: Any,
        identifiers: Dict[str, str],
        node_idx: int
    ) -> EvidenceNode:
        """Create an evidence node."""
        
        # Determine which identifier type for this level
        level = node_spec.level
        id_types_by_level = {
            0: ["ip_address", "mac_address", "badge_scan"],
            1: ["vpn_session", "connection_id", "badge_number"],
            2: ["user_id", "username", "device_id"],
            3: ["employee_number", "asset_tag"],
            4: ["name"]
        }
        
        possible_types = id_types_by_level.get(level, ["user_id"])
        identifier_type = random.choice(possible_types)
        identifier_value = identifiers.get(identifier_type, f"ID_{node_idx}")
        
        # Generate content
        content = self._generate_evidence_content(identifier_type, identifier_value)
        
        # Select document type
        category = self._get_category_for_identifier(identifier_type)
        doc_type = random.choice(self.doc_types.get(category, ["system_log"]))
        
        return EvidenceNode(
            node_id=node_id,
            evidence_type=EvidenceType.IDENTITY,
            content=content,
            identifier_type=identifier_type,
            identifier_value=identifier_value,
            assigned_doc_type=doc_type,
            isolated=True,
            importance="key",
            subgraph_id=subgraph_id
        )
    
    def _generate_evidence_content(self, identifier_type: str, identifier_value: str) -> str:
        """Generate natural-sounding evidence content."""
        templates = {
            "ip_address": f"Connection from IP {identifier_value} detected at 02:47:33",
            "mac_address": f"Network interface {identifier_value} active on subnet",
            "vpn_session": f"VPN session {identifier_value} established",
            "connection_id": f"Connection {identifier_value} initiated from external gateway",
            "user_id": f"User '{identifier_value}' authenticated successfully",
            "username": f"Login: {identifier_value} | Status: Active",
            "badge_number": f"Badge #{identifier_value} scanned at secure entrance",
            "badge_scan": f"Access granted: Badge {identifier_value}",
            "employee_number": f"Employee #{identifier_value} listed in personnel database",
            "device_id": f"Device {identifier_value} registered in IT asset system",
            "workstation_name": f"Workstation {identifier_value} logged system activity",
            "asset_tag": f"Asset tag: {identifier_value} | Status: Active",
            "name": f"Personnel record: {identifier_value}"
        }
        
        return templates.get(identifier_type, f"{identifier_type}: {identifier_value}")
    
    def _get_category_for_identifier(self, identifier_type: str) -> str:
        """Get category for identifier type."""
        for category, types in self.identifier_types.items():
            if identifier_type in types:
                return category
        return "system"
    
    def _create_inference_node(
        self,
        node_id: str,
        subgraph_id: str,
        node_spec: Any,
        evidence_nodes: List[EvidenceNode],
        inference_nodes: List[InferenceNode],
        target_name: str
    ) -> InferenceNode:
        """Create an inference node."""
        
        # Get parent nodes
        parent_ids = []
        for parent_idx in node_spec.parent_indices:
            # Parent could be evidence or inference
            if parent_idx < len(evidence_nodes) + len(inference_nodes):
                all_nodes = [e.node_id for e in evidence_nodes] + [i.node_id for i in inference_nodes]
                if parent_idx < len(all_nodes):
                    parent_ids.append(all_nodes[parent_idx])
        
        # Generate inference text
        inference = self._generate_inference_text(
            evidence_nodes,
            inference_nodes,
            node_spec,
            target_name
        )
        
        return InferenceNode(
            node_id=node_id,
            inference=inference,
            reasoning_type="cross_reference",
            parent_node_ids=parent_ids,
            required_document_ids=[],  # Will be filled later
            contributes_to=None,  # Will be set by subgraph
            subgraph_id=subgraph_id
        )
    
    def _generate_inference_text(
        self,
        evidence_nodes: List[EvidenceNode],
        inference_nodes: List[InferenceNode],
        node_spec: Any,
        target_name: str
    ) -> str:
        """Generate inference text."""
        level = node_spec.level
        
        # Final inference should mention the name
        if level >= 5 or (evidence_nodes and any("name" in e.identifier_type for e in evidence_nodes[-1:])):
            return f"Cross-referencing evidence leads to {target_name}"
        
        # Mid-level inferences connect identifiers
        inference_templates = [
            "Network activity correlates with authentication records",
            "Physical access logs match system login timestamps",
            "Device registration connects to employee database",
            "User credentials link to personnel records",
            "Badge access aligns with workstation activity"
        ]
        
        return random.choice(inference_templates)

