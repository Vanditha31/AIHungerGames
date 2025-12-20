"""Event schemas for AI Hunger Games observability.

Defines immutable event types that capture all arena behavior
for logging and replay. Events are structured data, not free-form strings.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RoundStartedEvent:
    """Event emitted when a round starts."""
    
    round_number: int
    prompt: str
    timestamp: str


@dataclass(frozen=True)
class AgentRespondedEvent:
    """Event emitted when an agent responds."""
    
    round_number: int
    agent_id: str
    response: str
    timestamp: str


@dataclass(frozen=True)
class VoteCastEvent:
    """Event emitted when a vote is cast.
    
    Per scope, only opaque agent IDs are logged, not responses.
    """
    
    round_number: int
    voter_id: str
    voted_for_id: str
    timestamp: str


@dataclass(frozen=True)
class VoteSummaryEvent:
    """Event emitted with aggregated vote results."""
    
    round_number: int
    vote_counts: dict[str, int]  # agent_id -> votes_received
    timestamp: str


@dataclass(frozen=True)
class EliminationDecidedEvent:
    """Event emitted when elimination is decided."""
    
    round_number: int
    eliminated_agent_id: str
    cumulative_votes: int
    was_tie: bool
    timestamp: str


@dataclass(frozen=True)
class AgentReplacedEvent:
    """Event emitted when an agent is replaced."""
    
    round_number: int
    agent_id: str
    old_personality: dict[str, Any]
    new_personality: dict[str, Any]
    timestamp: str


@dataclass(frozen=True)
class ArenaInitializedEvent:
    """Event emitted when arena is initialized."""
    
    num_agents: int
    agent_ids: list[str]
    settings: dict[str, Any]
    timestamp: str
