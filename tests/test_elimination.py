"""Tests for elimination logic module."""

import pytest

from ai_hunger_games.arena.elimination import (
    EliminationCandidate,
    determine_elimination,
)


class TestDetermineElimination:
    """Tests for determine_elimination function."""
    
    def test_eliminate_highest_votes(self) -> None:
        """Test that agent with highest votes is eliminated."""
        candidates = [
            EliminationCandidate("agent_1", cumulative_votes=5, historical_average=1.5),
            EliminationCandidate("agent_2", cumulative_votes=10, historical_average=2.0),
            EliminationCandidate("agent_3", cumulative_votes=3, historical_average=1.0),
        ]
        
        result = determine_elimination(candidates, seed=42)
        
        assert result.eliminated_agent_id == "agent_2"
        assert result.cumulative_votes == 10
        assert result.was_tie is False
    
    def test_tie_broken_by_historical_average(self) -> None:
        """Test that ties are broken by lowest historical average."""
        candidates = [
            EliminationCandidate("agent_1", cumulative_votes=10, historical_average=2.0),
            EliminationCandidate("agent_2", cumulative_votes=10, historical_average=1.5),
            EliminationCandidate("agent_3", cumulative_votes=5, historical_average=1.0),
        ]
        
        result = determine_elimination(candidates, seed=42)
        
        # agent_2 has same votes as agent_1 but lower historical average
        assert result.eliminated_agent_id == "agent_2"
        assert result.was_tie is True
    
    def test_tie_broken_by_seed(self) -> None:
        """Test that final tie is broken deterministically by seed."""
        candidates = [
            EliminationCandidate("agent_1", cumulative_votes=10, historical_average=2.0),
            EliminationCandidate("agent_2", cumulative_votes=10, historical_average=2.0),
            EliminationCandidate("agent_3", cumulative_votes=5, historical_average=1.0),
        ]
        
        result1 = determine_elimination(candidates, seed=42)
        result2 = determine_elimination(candidates, seed=42)
        result3 = determine_elimination(candidates, seed=99)
        
        # Same seed should give same result
        assert result1.eliminated_agent_id == result2.eliminated_agent_id
        assert result1.was_tie is True
        
        # Different seed might give different result (not guaranteed but likely)
        # Just verify it's still one of the tied candidates
        assert result3.eliminated_agent_id in ["agent_1", "agent_2"]
    
    def test_single_candidate(self) -> None:
        """Test with only one candidate."""
        candidates = [
            EliminationCandidate("agent_1", cumulative_votes=5, historical_average=1.0),
        ]
        
        result = determine_elimination(candidates, seed=42)
        
        assert result.eliminated_agent_id == "agent_1"
        assert result.was_tie is False
    
    def test_empty_candidates_raises(self) -> None:
        """Test that empty candidate list raises error."""
        with pytest.raises(ValueError, match="no candidates"):
            determine_elimination([], seed=42)
    
    def test_all_same_votes_and_average(self) -> None:
        """Test when all candidates have identical scores."""
        candidates = [
            EliminationCandidate("agent_1", cumulative_votes=5, historical_average=1.0),
            EliminationCandidate("agent_2", cumulative_votes=5, historical_average=1.0),
            EliminationCandidate("agent_3", cumulative_votes=5, historical_average=1.0),
        ]
        
        result = determine_elimination(candidates, seed=42)
        
        # Should deterministically pick one
        assert result.eliminated_agent_id in ["agent_1", "agent_2", "agent_3"]
        assert result.cumulative_votes == 5
        assert result.was_tie is True


class TestEliminationCandidate:
    """Tests for EliminationCandidate dataclass."""
    
    def test_create_candidate(self) -> None:
        """Test creating an elimination candidate."""
        candidate = EliminationCandidate(
            agent_id="agent_1",
            cumulative_votes=10,
            historical_average=2.5
        )
        
        assert candidate.agent_id == "agent_1"
        assert candidate.cumulative_votes == 10
        assert candidate.historical_average == 2.5
    
    def test_candidate_is_frozen(self) -> None:
        """Test that candidates cannot be modified."""
        candidate = EliminationCandidate(
            agent_id="agent_1",
            cumulative_votes=10,
            historical_average=2.5
        )
        
        with pytest.raises(AttributeError):
            candidate.cumulative_votes = 15
