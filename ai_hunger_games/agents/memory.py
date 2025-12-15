"""Memory management for AI Hunger Games agents.

Agents have read-only access to their own history via a sliding window.
Memory includes previous answers, votes cast, and aggregate voting outcomes.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class VoteCounts:
    """Aggregate voting outcomes for a round (counts only, no identities).
    
    Per ARCHITECTURE.md, agents only see aggregate counts, not who voted.
    """
    
    total_votes: int
    votes_received: int


@dataclass(frozen=True)
class MemoryEntry:
    """A single memory entry representing one round's activity.
    
    Contains the agent's own response and vote, plus aggregate outcomes.
    Does NOT contain other agents' responses per Forbidden Patterns.
    """
    
    round_number: int
    prompt: str
    response: str
    vote_cast: Optional[str] = None  # agent_id voted for, None if no vote yet
    vote_counts: Optional[VoteCounts] = None  # aggregate outcomes


class AgentMemory:
    """Sliding window memory for an agent.
    
    Maintains a fixed-size window of recent round entries.
    Memory is append-only during a run; old entries are dropped
    when the window size is exceeded.
    """
    
    def __init__(self, window_size: int = 5) -> None:
        """Initialize agent memory with specified window size.
        
        Args:
            window_size: Maximum number of rounds to remember.
        """
        if window_size < 1:
            raise ValueError("Memory window size must be at least 1")
        
        self._window_size = window_size
        self._entries: list[MemoryEntry] = []
    
    @property
    def window_size(self) -> int:
        """Get the configured window size."""
        return self._window_size
    
    def add_entry(self, entry: MemoryEntry) -> None:
        """Add a new memory entry, dropping oldest if window exceeded.
        
        Args:
            entry: The memory entry to add.
        """
        self._entries.append(entry)
        
        if len(self._entries) > self._window_size:
            self._entries = self._entries[-self._window_size:]
    
    def get_entries(self) -> list[MemoryEntry]:
        """Get all entries in the memory window.
        
        Returns:
            List of memory entries, oldest first.
        """
        return list(self._entries)
    
    def get_latest(self) -> Optional[MemoryEntry]:
        """Get the most recent memory entry.
        
        Returns:
            Latest entry or None if memory is empty.
        """
        if not self._entries:
            return None
        return self._entries[-1]
    
    def count(self) -> int:
        """Get the number of entries currently in memory.
        
        Returns:
            Number of stored entries.
        """
        return len(self._entries)
    
    def clear(self) -> None:
        """Clear all memory entries."""
        self._entries = []
