"""Sub-graph architecture types for evidence chains."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class SubGraphPattern(Enum):
    """Pre-defined patterns for sub-graph structures."""
    LINEAR = "linear"  # A → B → C → D
    BRANCHING = "branching"  # A → B, C → D (converge at D)
    PARALLEL = "parallel"  # A → B and C → D (independent)
    CONVERGENT = "convergent"  # A, B, C → D (all lead to same conclusion)


@dataclass
class NodeSpec:
    """Specification for a node in a sub-graph."""
    node_type: str  # evidence, inference
    content_type: str  # identity, psychological, crypto
    level: int  # Position in chain (0 = start, higher = later)
    parent_indices: List[int] = field(default_factory=list)  # Which nodes this depends on


@dataclass
class SubGraphArchitecture:
    """Architecture template for a sub-graph."""
    
    name: str
    pattern: SubGraphPattern
    evidence_type: str  # identity, psychological, cryptographic
    
    # Node specifications
    nodes: List[NodeSpec] = field(default_factory=list)
    
    # Metadata
    min_hops: int = 3
    max_hops: int = 8
    difficulty: int = 5
    
    # Answer contribution
    contributes_to: Optional[str] = None  # WHO, WHAT, WHY, HOW


# Identity sub-graph architectures
IDENTITY_LINEAR = SubGraphArchitecture(
    name="identity_linear",
    pattern=SubGraphPattern.LINEAR,
    evidence_type="identity",
    nodes=[
        NodeSpec(node_type="evidence", content_type="identity", level=0),  # IP address
        NodeSpec(node_type="evidence", content_type="identity", level=1),  # Session ID
        NodeSpec(node_type="inference", content_type="identity", level=2, parent_indices=[0, 1]),  # IP → Session
        NodeSpec(node_type="evidence", content_type="identity", level=2),  # User ID
        NodeSpec(node_type="inference", content_type="identity", level=3, parent_indices=[2, 3]),  # Session → User
        NodeSpec(node_type="evidence", content_type="identity", level=3),  # Employee ID
        NodeSpec(node_type="inference", content_type="identity", level=4, parent_indices=[4, 5]),  # User → Employee
        NodeSpec(node_type="evidence", content_type="identity", level=4),  # Name
        NodeSpec(node_type="inference", content_type="identity", level=5, parent_indices=[6, 7]),  # Employee → Name
    ],
    min_hops=4,
    max_hops=6,
    contributes_to="WHO"
)

IDENTITY_BRANCHING = SubGraphArchitecture(
    name="identity_branching",
    pattern=SubGraphPattern.BRANCHING,
    evidence_type="identity",
    nodes=[
        # Branch 1: Network path
        NodeSpec(node_type="evidence", content_type="identity", level=0),  # IP
        NodeSpec(node_type="evidence", content_type="identity", level=1),  # VPN session
        NodeSpec(node_type="inference", content_type="identity", level=2, parent_indices=[0, 1]),  # IP → VPN
        
        # Branch 2: Physical path
        NodeSpec(node_type="evidence", content_type="identity", level=0),  # Badge scan
        NodeSpec(node_type="evidence", content_type="identity", level=1),  # Location
        NodeSpec(node_type="inference", content_type="identity", level=2, parent_indices=[3, 4]),  # Badge → Location
        
        # Convergence
        NodeSpec(node_type="evidence", content_type="identity", level=3),  # Employee ID (both paths lead here)
        NodeSpec(node_type="inference", content_type="identity", level=4, parent_indices=[2, 5, 6]),  # All → Employee
        NodeSpec(node_type="evidence", content_type="identity", level=4),  # Name
        NodeSpec(node_type="inference", content_type="identity", level=5, parent_indices=[7, 8]),  # Employee → Name
    ],
    min_hops=5,
    max_hops=7,
    contributes_to="WHO"
)

# Psychological sub-graph architectures
PSYCHOLOGICAL_PATTERN = SubGraphArchitecture(
    name="psychological_pattern",
    pattern=SubGraphPattern.LINEAR,
    evidence_type="psychological",
    nodes=[
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # Behavior observation 1
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # Behavior observation 2
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # Behavior observation 3
        NodeSpec(node_type="inference", content_type="psychological", level=1, parent_indices=[0, 1, 2]),  # Pattern
        NodeSpec(node_type="evidence", content_type="psychological", level=2),  # Motive clue
        NodeSpec(node_type="inference", content_type="psychological", level=3, parent_indices=[3, 4]),  # Motive inference
        NodeSpec(node_type="evidence", content_type="psychological", level=3),  # Role evidence
        NodeSpec(node_type="inference", content_type="psychological", level=4, parent_indices=[5, 6]),  # Role conclusion
    ],
    min_hops=4,
    max_hops=6,
    contributes_to="WHY"
)

PSYCHOLOGICAL_RELATIONSHIP = SubGraphArchitecture(
    name="psychological_relationship",
    pattern=SubGraphPattern.CONVERGENT,
    evidence_type="psychological",
    nodes=[
        # Person A indicators
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # A's stress
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # A's communications
        
        # Person B indicators
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # B's paranoia
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # B's actions
        
        # Relationship inference
        NodeSpec(node_type="inference", content_type="psychological", level=1, parent_indices=[0, 1, 2, 3]),  # Relationship pattern
        NodeSpec(node_type="evidence", content_type="psychological", level=2),  # Shared motivation
        NodeSpec(node_type="inference", content_type="psychological", level=3, parent_indices=[4, 5]),  # Collusion inference
    ],
    min_hops=3,
    max_hops=5,
    contributes_to="WHO"
)

# Cryptographic sub-graph architectures
CRYPTO_LINEAR = SubGraphArchitecture(
    name="crypto_linear",
    pattern=SubGraphPattern.LINEAR,
    evidence_type="cryptographic",
    nodes=[
        NodeSpec(node_type="evidence", content_type="crypto", level=0),  # Encrypted phrase
        NodeSpec(node_type="evidence", content_type="crypto", level=1),  # Key hint
        NodeSpec(node_type="evidence", content_type="crypto", level=2),  # Character backstory detail
        NodeSpec(node_type="inference", content_type="crypto", level=3, parent_indices=[1, 2]),  # Infer key
        NodeSpec(node_type="inference", content_type="crypto", level=4, parent_indices=[0, 3]),  # Decrypt message
        NodeSpec(node_type="inference", content_type="crypto", level=5, parent_indices=[4]),  # Interpret decoded message
    ],
    min_hops=3,
    max_hops=5,
    contributes_to="WHAT"
)

CRYPTO_MULTI_KEY = SubGraphArchitecture(
    name="crypto_multi_key",
    pattern=SubGraphPattern.CONVERGENT,
    evidence_type="cryptographic",
    nodes=[
        # Encrypted message
        NodeSpec(node_type="evidence", content_type="crypto", level=0),  # Encrypted phrase
        
        # Key path 1
        NodeSpec(node_type="evidence", content_type="crypto", level=1),  # Hint 1
        NodeSpec(node_type="evidence", content_type="crypto", level=1),  # Character detail 1
        NodeSpec(node_type="inference", content_type="crypto", level=2, parent_indices=[1, 2]),  # Partial key 1
        
        # Key path 2
        NodeSpec(node_type="evidence", content_type="crypto", level=1),  # Hint 2
        NodeSpec(node_type="evidence", content_type="crypto", level=1),  # Character detail 2
        NodeSpec(node_type="inference", content_type="crypto", level=2, parent_indices=[4, 5]),  # Partial key 2
        
        # Combine keys
        NodeSpec(node_type="inference", content_type="crypto", level=3, parent_indices=[3, 6]),  # Full key
        NodeSpec(node_type="inference", content_type="crypto", level=4, parent_indices=[0, 7]),  # Decrypt
        NodeSpec(node_type="inference", content_type="crypto", level=5, parent_indices=[8]),  # Interpret
    ],
    min_hops=5,
    max_hops=7,
    contributes_to="HOW"
)

# Red herring architectures
RED_HERRING_BROKEN = SubGraphArchitecture(
    name="red_herring_broken",
    pattern=SubGraphPattern.LINEAR,
    evidence_type="identity",
    nodes=[
        NodeSpec(node_type="evidence", content_type="identity", level=0),  # Plausible start
        NodeSpec(node_type="evidence", content_type="identity", level=1),  # Seems connected
        NodeSpec(node_type="inference", content_type="identity", level=2, parent_indices=[0, 1]),  # Partial connection
        # Missing node here - chain breaks
        NodeSpec(node_type="evidence", content_type="identity", level=3),  # Dead end (wrong person)
    ],
    min_hops=2,
    max_hops=3,
    contributes_to=None  # Doesn't contribute - it's false
)

RED_HERRING_MISDIRECTION = SubGraphArchitecture(
    name="red_herring_misdirection",
    pattern=SubGraphPattern.LINEAR,
    evidence_type="psychological",
    nodes=[
        NodeSpec(node_type="evidence", content_type="psychological", level=0),  # Suspicious behavior
        NodeSpec(node_type="evidence", content_type="psychological", level=1),  # Motive (but wrong person)
        NodeSpec(node_type="inference", content_type="psychological", level=2, parent_indices=[0, 1]),  # False conclusion
    ],
    min_hops=2,
    max_hops=3,
    contributes_to=None
)


# All available architectures
ALL_ARCHITECTURES = {
    "identity": [IDENTITY_LINEAR, IDENTITY_BRANCHING],
    "psychological": [PSYCHOLOGICAL_PATTERN, PSYCHOLOGICAL_RELATIONSHIP],
    "cryptographic": [CRYPTO_LINEAR, CRYPTO_MULTI_KEY],
    "red_herring": [RED_HERRING_BROKEN, RED_HERRING_MISDIRECTION]
}


def get_architecture_for_type(evidence_type: str, difficulty: int) -> SubGraphArchitecture:
    """
    Get an appropriate architecture for evidence type and difficulty.
    
    Args:
        evidence_type: Type of evidence (identity, psychological, cryptographic, red_herring)
        difficulty: Difficulty level (1-10)
    
    Returns:
        SubGraphArchitecture
    """
    import random
    
    architectures = ALL_ARCHITECTURES.get(evidence_type, ALL_ARCHITECTURES["identity"])
    
    # Higher difficulty = prefer more complex patterns
    if difficulty >= 7 and len(architectures) > 1:
        # Prefer branching/convergent for high difficulty
        return architectures[-1]
    
    return random.choice(architectures)

