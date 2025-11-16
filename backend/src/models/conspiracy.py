"""Conspiracy mystery data models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib


class EvidenceType(Enum):
    """Types of evidence in sub-graphs."""
    IDENTITY = "identity"  # Technical chains (60%)
    PSYCHOLOGICAL = "psychological"  # Behavioral patterns (20%)
    CRYPTOGRAPHIC = "cryptographic"  # Encrypted evidence (20%)
    RED_HERRING = "red_herring"  # False paths


class NodeType(Enum):
    """Types of nodes in sub-graphs."""
    EVIDENCE = "evidence"  # Leaf node - raw data
    INFERENCE = "inference"  # Derived from evidence
    CONCLUSION = "conclusion"  # Final answer component


class AnswerDimension(Enum):
    """Four dimensions of conspiracy answer."""
    WHO = "who"  # The conspirators
    WHAT = "what"  # The conspiracy goal
    WHY = "why"  # The motivation
    HOW = "how"  # The method


@dataclass
class MysteryAnswer:
    """4-blank answer template for mystery submission."""
    
    # Canonical answers (discoverable through investigation)
    who: str = ""          # Conspirator name (e.g., "Dr. Liora Vance")
    what: str = ""         # Operation name (e.g., "Eclipse Veil")
    why: str = ""          # Motivation (e.g., "Awaken Void Serpent")
    how: str = ""          # Method/tactics (e.g., "Infiltrate Government")
    
    # Combined hash for contract
    combined_hash: str = ""
    
    def generate_hash(self) -> str:
        """Generate combined hash matching contract logic."""
        combined = f"{self.who.lower()}|{self.what.lower()}|{self.why.lower()}|{self.how.lower()}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "who": self.who,
            "what": self.what,
            "why": self.why,
            "how": self.how,
            "combined_hash": self.combined_hash
        }


@dataclass
class PoliticalContext:
    """Fictional political/institutional backdrop for conspiracy."""
    
    # Core context
    world_name: str = "The Republic"
    time_period: str = "Present Day"
    
    # Institutions
    shadow_agencies: List[Dict[str, str]] = field(default_factory=list)  # name, role, agenda
    secret_services: List[Dict[str, str]] = field(default_factory=list)
    military_branches: List[Dict[str, str]] = field(default_factory=list)
    corporations: List[Dict[str, str]] = field(default_factory=list)
    occult_organizations: List[Dict[str, str]] = field(default_factory=list)
    
    # Power dynamics
    competing_factions: List[Dict[str, Any]] = field(default_factory=list)  # faction, rivals, goals
    alliances: List[Dict[str, str]] = field(default_factory=list)  # faction1, faction2, nature
    
    # Historical backdrop
    past_events: List[Dict[str, str]] = field(default_factory=list)  # event, date, impact
    cover_ups: List[Dict[str, str]] = field(default_factory=list)
    unresolved_tensions: List[str] = field(default_factory=list)
    
    # Geopolitical
    resource_conflicts: List[str] = field(default_factory=list)
    ideological_tensions: List[str] = field(default_factory=list)
    
    # Narrative layers
    public_narrative: str = ""  # What people believe
    hidden_reality: str = ""  # What's actually happening
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "world_name": self.world_name,
            "time_period": self.time_period,
            "shadow_agencies": self.shadow_agencies,
            "secret_services": self.secret_services,
            "military_branches": self.military_branches,
            "corporations": self.corporations,
            "occult_organizations": self.occult_organizations,
            "competing_factions": self.competing_factions,
            "alliances": self.alliances,
            "past_events": self.past_events,
            "cover_ups": self.cover_ups,
            "unresolved_tensions": self.unresolved_tensions,
            "resource_conflicts": self.resource_conflicts,
            "ideological_tensions": self.ideological_tensions,
            "public_narrative": self.public_narrative,
            "hidden_reality": self.hidden_reality
        }


@dataclass
class ConspiracyPremise:
    """Four-dimensional conspiracy answer structure."""
    
    # The four answers
    who: str  # Who are the conspirators (names)
    what: str  # What is the conspiracy goal
    why: str  # Why are they doing it (motivation)
    how: str  # How are they doing it (method)
    
    # Context
    conspiracy_name: str = "Operation Unknown"
    conspiracy_type: str = "occult"  # occult, secret_society, underground_network
    
    # Metadata
    difficulty: int = 5
    political_context_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "who": self.who,
            "what": self.what,
            "why": self.why,
            "how": self.how,
            "conspiracy_name": self.conspiracy_name,
            "conspiracy_type": self.conspiracy_type,
            "difficulty": self.difficulty,
            "political_context_id": self.political_context_id
        }


@dataclass
class EvidenceNode:
    """A node in an evidence sub-graph (raw data)."""
    
    node_id: str
    evidence_type: EvidenceType
    content: str  # The actual evidence
    
    # Technical details (for identity chains)
    identifier_type: Optional[str] = None  # ip, session, badge, user_id, etc.
    identifier_value: Optional[str] = None
    
    # Psychological details
    psychological_indicator: Optional[str] = None  # stress, paranoia, deception, etc.
    
    # Crypto details
    encrypted_phrase: Optional[str] = None
    encryption_type: Optional[str] = None  # caesar, vigenere, substitution
    key_hint: Optional[str] = None  # Where to find the key
    
    # Document assignment
    assigned_doc_type: Optional[str] = None  # What document type this belongs in
    
    # Isolation
    isolated: bool = True  # Must be in its own document/section
    
    # Metadata
    importance: str = "key"  # key, supporting, minor
    subgraph_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "evidence_type": self.evidence_type.value,
            "content": self.content,
            "identifier_type": self.identifier_type,
            "identifier_value": self.identifier_value,
            "psychological_indicator": self.psychological_indicator,
            "encrypted_phrase": self.encrypted_phrase,
            "encryption_type": self.encryption_type,
            "key_hint": self.key_hint,
            "assigned_doc_type": self.assigned_doc_type,
            "isolated": self.isolated,
            "importance": self.importance,
            "subgraph_id": self.subgraph_id
        }


@dataclass
class InferenceNode:
    """A node representing an inference/conclusion from evidence."""
    
    node_id: str
    inference: str  # The conclusion
    reasoning_type: str  # cross_reference, temporal, deduction, synthesis
    
    # Dependencies
    parent_node_ids: List[str] = field(default_factory=list)  # Nodes this depends on
    required_document_ids: List[str] = field(default_factory=list)
    
    # Answer contribution
    contributes_to: Optional[AnswerDimension] = None  # WHO, WHAT, WHY, HOW
    
    # Metadata
    subgraph_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "inference": self.inference,
            "reasoning_type": self.reasoning_type,
            "parent_node_ids": self.parent_node_ids,
            "required_document_ids": self.required_document_ids,
            "contributes_to": self.contributes_to.value if self.contributes_to else None,
            "subgraph_id": self.subgraph_id
        }


@dataclass
class SubGraph:
    """A chain of evidence leading to a conclusion (or dead end)."""
    
    subgraph_id: str
    subgraph_type: EvidenceType
    
    # Nodes
    evidence_nodes: List[EvidenceNode] = field(default_factory=list)
    inference_nodes: List[InferenceNode] = field(default_factory=list)
    
    # Structure
    conclusion: Optional[str] = None  # Final conclusion (if complete)
    is_complete: bool = True  # False for red herrings
    is_red_herring: bool = False
    
    # Convergence
    contributes_to: Optional[AnswerDimension] = None
    
    # Metadata
    hop_count: int = 0  # Number of inference steps
    difficulty: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subgraph_id": self.subgraph_id,
            "subgraph_type": self.subgraph_type.value,
            "evidence_nodes": [node.to_dict() for node in self.evidence_nodes],
            "inference_nodes": [node.to_dict() for node in self.inference_nodes],
            "conclusion": self.conclusion,
            "is_complete": self.is_complete,
            "is_red_herring": self.is_red_herring,
            "contributes_to": self.contributes_to.value if self.contributes_to else None,
            "hop_count": self.hop_count,
            "difficulty": self.difficulty
        }


@dataclass
class CryptoKey:
    """Inference-based cryptographic key."""
    
    key_id: str
    key_value: str  # The actual key
    
    # Inference required
    inference_description: str  # "what father always said about trust"
    character_name: Optional[str] = None  # Whose backstory contains the key
    
    # Location hints
    hint_documents: List[str] = field(default_factory=list)  # Where hints appear
    discoverable: bool = True
    
    # Linked evidence
    unlocks_node_id: Optional[str] = None  # Which encrypted node this unlocks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key_id": self.key_id,
            "key_value": self.key_value,
            "inference_description": self.inference_description,
            "character_name": self.character_name,
            "hint_documents": self.hint_documents,
            "discoverable": self.discoverable,
            "unlocks_node_id": self.unlocks_node_id
        }


@dataclass
class DocumentAssignment:
    """Maps sub-graph nodes to documents."""
    
    document_id: str
    document_type: str
    
    # Assigned nodes
    evidence_node_ids: List[str] = field(default_factory=list)
    inference_node_ids: List[str] = field(default_factory=list)
    
    # Subgraphs referenced
    subgraph_ids: List[str] = field(default_factory=list)
    
    # Constraints
    max_nodes: int = 3  # Maximum nodes per document
    requires_cross_reference: bool = False  # Must reference other documents
    
    # Crypto
    contains_encrypted_phrase: bool = False
    contains_crypto_key: bool = False
    
    # Answer containment (algorithmic enforcement)
    can_contain_who_answer: bool = True  # Can include primary conspirator's full name
    can_contain_what_answer: bool = True  # Can include full operation codename
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "document_type": self.document_type,
            "evidence_node_ids": self.evidence_node_ids,
            "inference_node_ids": self.inference_node_ids,
            "subgraph_ids": self.subgraph_ids,
            "max_nodes": self.max_nodes,
            "requires_cross_reference": self.requires_cross_reference,
            "contains_encrypted_phrase": self.contains_encrypted_phrase,
            "contains_crypto_key": self.contains_crypto_key
        }


@dataclass
class ImageClue:
    """Visual evidence in images."""
    
    image_id: str
    image_type: str  # photograph, document, symbol, object
    
    # Content
    description: str
    visual_clues: List[str] = field(default_factory=list)  # What clues are visible
    
    # Linked evidence
    evidence_node_ids: List[str] = field(default_factory=list)
    subgraph_id: Optional[str] = None
    
    # Generation
    prompt: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "image_id": self.image_id,
            "image_type": self.image_type,
            "description": self.description,
            "visual_clues": self.visual_clues,
            "evidence_node_ids": self.evidence_node_ids,
            "subgraph_id": self.subgraph_id,
            "prompt": self.prompt
        }


@dataclass
class ConspiracyMystery:
    """Complete conspiracy mystery with all components."""
    
    # Core
    mystery_id: str
    political_context: PoliticalContext
    premise: ConspiracyPremise
    
    # Answer template (for submission)
    answer_template: Optional[MysteryAnswer] = None
    
    # Questions (tailored to conspiracy)
    questions: Optional[Dict[str, str]] = None
    
    # Evidence structure
    subgraphs: List[SubGraph] = field(default_factory=list)
    crypto_keys: List[CryptoKey] = field(default_factory=list)
    
    # Document mapping
    document_assignments: List[DocumentAssignment] = field(default_factory=list)
    
    # Visual evidence
    image_clues: List[ImageClue] = field(default_factory=list)
    
    # Generated content (populated later)
    characters: List[Dict[str, Any]] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    locations: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    difficulty: int = 5
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mystery_id": self.mystery_id,
            "political_context": self.political_context.to_dict(),
            "premise": self.premise.to_dict(),
            "answer_template": self.answer_template.to_dict() if self.answer_template else None,
            "questions": self.questions,
            "subgraphs": [sg.to_dict() for sg in self.subgraphs],
            "crypto_keys": [ck.to_dict() for ck in self.crypto_keys],
            "document_assignments": [da.to_dict() for da in self.document_assignments],
            "image_clues": [ic.to_dict() for ic in self.image_clues],
            "characters": self.characters,
            "timeline": self.timeline,
            "locations": self.locations,
            "documents": self.documents,
            "difficulty": self.difficulty,
            "created_at": self.created_at
        }

