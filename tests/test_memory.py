"""Tests for agent memory module."""

import pytest

from ai_hunger_games.agents.memory import AgentMemory, MemoryEntry, VoteCounts


class TestVoteCounts:
    """Tests for VoteCounts dataclass."""
    
    def test_create_vote_counts(self) -> None:
        """Test creating vote counts."""
        counts = VoteCounts(total_votes=8, votes_received=2)
        
        assert counts.total_votes == 8
        assert counts.votes_received == 2
    
    def test_vote_counts_is_frozen(self) -> None:
        """Test that vote counts cannot be modified."""
        counts = VoteCounts(total_votes=8, votes_received=2)
        
        with pytest.raises(AttributeError):
            counts.total_votes = 10


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""
    
    def test_create_minimal_entry(self) -> None:
        """Test creating entry with required fields only."""
        entry = MemoryEntry(
            round_number=1,
            prompt="Test prompt",
            response="Test response"
        )
        
        assert entry.round_number == 1
        assert entry.prompt == "Test prompt"
        assert entry.response == "Test response"
        assert entry.vote_cast is None
        assert entry.vote_counts is None
    
    def test_create_full_entry(self) -> None:
        """Test creating entry with all fields."""
        counts = VoteCounts(total_votes=8, votes_received=1)
        entry = MemoryEntry(
            round_number=5,
            prompt="Another prompt",
            response="My response",
            vote_cast="agent_3",
            vote_counts=counts
        )
        
        assert entry.round_number == 5
        assert entry.vote_cast == "agent_3"
        assert entry.vote_counts.total_votes == 8
    
    def test_memory_entry_is_frozen(self) -> None:
        """Test that memory entry cannot be modified."""
        entry = MemoryEntry(
            round_number=1,
            prompt="Test",
            response="Response"
        )
        
        with pytest.raises(AttributeError):
            entry.round_number = 2


class TestAgentMemory:
    """Tests for AgentMemory class."""
    
    def test_create_memory_with_default_window(self) -> None:
        """Test creating memory with default window size."""
        memory = AgentMemory()
        
        assert memory.window_size == 5
        assert memory.count() == 0
    
    def test_create_memory_with_custom_window(self) -> None:
        """Test creating memory with custom window size."""
        memory = AgentMemory(window_size=10)
        
        assert memory.window_size == 10
    
    def test_invalid_window_size(self) -> None:
        """Test that window size must be positive."""
        with pytest.raises(ValueError, match="at least 1"):
            AgentMemory(window_size=0)
        
        with pytest.raises(ValueError, match="at least 1"):
            AgentMemory(window_size=-1)
    
    def test_add_and_get_entries(self) -> None:
        """Test adding and retrieving entries."""
        memory = AgentMemory(window_size=5)
        
        entry1 = MemoryEntry(round_number=1, prompt="P1", response="R1")
        entry2 = MemoryEntry(round_number=2, prompt="P2", response="R2")
        
        memory.add_entry(entry1)
        memory.add_entry(entry2)
        
        entries = memory.get_entries()
        assert len(entries) == 2
        assert entries[0].round_number == 1
        assert entries[1].round_number == 2
    
    def test_sliding_window(self) -> None:
        """Test that old entries are dropped when window exceeded."""
        memory = AgentMemory(window_size=3)
        
        for i in range(5):
            entry = MemoryEntry(round_number=i + 1, prompt=f"P{i}", response=f"R{i}")
            memory.add_entry(entry)
        
        entries = memory.get_entries()
        assert len(entries) == 3
        assert entries[0].round_number == 3
        assert entries[1].round_number == 4
        assert entries[2].round_number == 5
    
    def test_get_latest(self) -> None:
        """Test getting the most recent entry."""
        memory = AgentMemory()
        
        assert memory.get_latest() is None
        
        entry1 = MemoryEntry(round_number=1, prompt="P1", response="R1")
        entry2 = MemoryEntry(round_number=2, prompt="P2", response="R2")
        
        memory.add_entry(entry1)
        assert memory.get_latest().round_number == 1
        
        memory.add_entry(entry2)
        assert memory.get_latest().round_number == 2
    
    def test_count(self) -> None:
        """Test counting entries."""
        memory = AgentMemory(window_size=5)
        
        assert memory.count() == 0
        
        for i in range(3):
            entry = MemoryEntry(round_number=i + 1, prompt=f"P{i}", response=f"R{i}")
            memory.add_entry(entry)
        
        assert memory.count() == 3
    
    def test_clear(self) -> None:
        """Test clearing memory."""
        memory = AgentMemory()
        
        entry = MemoryEntry(round_number=1, prompt="P", response="R")
        memory.add_entry(entry)
        assert memory.count() == 1
        
        memory.clear()
        assert memory.count() == 0
        assert memory.get_entries() == []
