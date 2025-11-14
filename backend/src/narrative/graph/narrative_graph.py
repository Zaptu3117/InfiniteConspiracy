"""Narrative graph data structures for story generation."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class Character:
    """A character in the mystery narrative."""
    
    name: str
    role: str
    background: str
    personality: str
    relationships: Dict[str, str] = field(default_factory=dict)
    access_level: List[str] = field(default_factory=list)
    secrets: str = ""
    motivation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "background": self.background,
            "personality": self.personality,
            "relationships": self.relationships,
            "access_level": self.access_level,
            "secrets": self.secrets,
            "motivation": self.motivation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class TimelineEvent:
    """An event in the mystery timeline."""
    
    timestamp: str
    event_type: str
    description: str
    participants: List[str]
    location: str
    evidence_created: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "description": self.description,
            "participants": self.participants,
            "location": self.location,
            "evidence_created": self.evidence_created
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineEvent':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Location:
    """A location in the mystery setting."""
    
    name: str
    type: str
    description: str
    access_requirements: List[str] = field(default_factory=list)
    security_level: str = "public"
    surveillance: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "access_requirements": self.access_requirements,
            "security_level": self.security_level,
            "surveillance": self.surveillance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ClueAssignment:
    """A clue to be embedded in a document."""
    
    clue_id: str
    clue_data: str
    field_to_insert: str
    importance: str = "key"  # key, supporting, red_herring
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "clue_id": self.clue_id,
            "clue_data": self.clue_data,
            "field_to_insert": self.field_to_insert,
            "importance": self.importance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClueAssignment':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Reference:
    """A reference from one document to another."""
    
    target_doc_id: str
    reference_type: str  # explicit, implicit, temporal
    context: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "target_doc_id": self.target_doc_id,
            "reference_type": self.reference_type,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reference':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DocumentPlan:
    """Plan for a document to be generated."""
    
    doc_id: str
    doc_type: str
    author: str
    timestamp: str
    clues_to_include: List[ClueAssignment] = field(default_factory=list)
    purpose: str = ""
    is_red_herring: bool = False
    references: List[Reference] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "doc_type": self.doc_type,
            "author": self.author,
            "timestamp": self.timestamp,
            "clues_to_include": [clue.to_dict() for clue in self.clues_to_include],
            "purpose": self.purpose,
            "is_red_herring": self.is_red_herring,
            "references": [ref.to_dict() for ref in self.references]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentPlan':
        """Create from dictionary."""
        clues = [ClueAssignment.from_dict(c) for c in data.get("clues_to_include", [])]
        refs = [Reference.from_dict(r) for r in data.get("references", [])]
        return cls(
            doc_id=data["doc_id"],
            doc_type=data["doc_type"],
            author=data["author"],
            timestamp=data["timestamp"],
            clues_to_include=clues,
            purpose=data.get("purpose", ""),
            is_red_herring=data.get("is_red_herring", False),
            references=refs
        )


@dataclass
class NarrativeGraph:
    """
    Complete narrative graph containing all story elements.
    Built up through 5-step narrator process.
    """
    
    # Core mystery
    mystery_question: str
    mystery_answer: str
    
    # Story elements (from 5 narrator steps)
    characters: List[Character] = field(default_factory=list)
    timeline: List[TimelineEvent] = field(default_factory=list)
    locations: List[Location] = field(default_factory=list)
    document_plan: List[DocumentPlan] = field(default_factory=list)
    
    # Metadata
    difficulty: int = 5
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def get_character(self, name: str) -> Optional[Character]:
        """Get character by name."""
        for char in self.characters:
            if char.name == name:
                return char
        return None
    
    def get_document_plan(self, doc_id: str) -> Optional[DocumentPlan]:
        """Get document plan by ID."""
        for doc in self.document_plan:
            if doc.doc_id == doc_id:
                return doc
        return None
    
    def get_referenced_documents(self, doc_id: str) -> List[DocumentPlan]:
        """Get all documents referenced by a given document."""
        doc = self.get_document_plan(doc_id)
        if not doc:
            return []
        
        referenced = []
        for ref in doc.references:
            ref_doc = self.get_document_plan(ref.target_doc_id)
            if ref_doc:
                referenced.append(ref_doc)
        return referenced
    
    def get_timeline_context(self, timestamp: str) -> List[TimelineEvent]:
        """Get all events before a given timestamp."""
        target_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        context_events = []
        
        for event in self.timeline:
            event_time = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
            if event_time < target_time:
                context_events.append(event)
        
        return sorted(context_events, key=lambda e: e.timestamp)
    
    def get_character_documents(self, character_name: str) -> List[DocumentPlan]:
        """Get all documents authored by a character."""
        return [doc for doc in self.document_plan if doc.author == character_name]
    
    def get_documents_with_clue(self, clue_id: str) -> List[DocumentPlan]:
        """Get all documents containing a specific clue."""
        docs = []
        for doc in self.document_plan:
            for clue in doc.clues_to_include:
                if clue.clue_id == clue_id:
                    docs.append(doc)
                    break
        return docs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "mystery_question": self.mystery_question,
            "mystery_answer": self.mystery_answer,
            "difficulty": self.difficulty,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "characters": [char.to_dict() for char in self.characters],
            "timeline": [event.to_dict() for event in self.timeline],
            "locations": [loc.to_dict() for loc in self.locations],
            "document_plan": [doc.to_dict() for doc in self.document_plan]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeGraph':
        """Create from dictionary."""
        characters = [Character.from_dict(c) for c in data.get("characters", [])]
        timeline = [TimelineEvent.from_dict(e) for e in data.get("timeline", [])]
        locations = [Location.from_dict(l) for l in data.get("locations", [])]
        document_plan = [DocumentPlan.from_dict(d) for d in data.get("document_plan", [])]
        
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        
        return cls(
            mystery_question=data["mystery_question"],
            mystery_answer=data["mystery_answer"],
            difficulty=data.get("difficulty", 5),
            created_at=created_at,
            characters=characters,
            timeline=timeline,
            locations=locations,
            document_plan=document_plan
        )
    
    def to_visualization(self) -> str:
        """Export as DOT format for visualization."""
        lines = ["digraph NarrativeGraph {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box];")
        lines.append("")
        
        # Add document nodes
        for doc in self.document_plan:
            color = "red" if doc.is_red_herring else "lightblue"
            lines.append(f'  "{doc.doc_id}" [label="{doc.doc_type}\\n{doc.author}", fillcolor={color}, style=filled];')
        
        lines.append("")
        
        # Add edges (references)
        for doc in self.document_plan:
            for ref in doc.references:
                style = "solid" if ref.reference_type == "explicit" else "dashed"
                lines.append(f'  "{doc.doc_id}" -> "{ref.target_doc_id}" [style={style}, label="{ref.reference_type}"];')
        
        lines.append("}")
        return "\n".join(lines)

