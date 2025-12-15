"""Tests for vote aggregation module."""

from ai_hunger_games.voting.aggregation import aggregate_votes
from ai_hunger_games.voting.types import Vote


class TestAggregateVotes:
    """Tests for aggregate_votes function."""
    
    def test_aggregate_simple_votes(self) -> None:
        """Test aggregating votes with no ties."""
        votes = [
            Vote("agent_1", "agent_2", 1),
            Vote("agent_2", "agent_3", 1),
            Vote("agent_3", "agent_2", 1),
        ]
        
        result = aggregate_votes(votes, 1, ["agent_1", "agent_2", "agent_3"])
        
        assert result.round_number == 1
        assert len(result.votes) == 3
        assert len(result.results) == 3
        
        # Check vote counts
        assert result.get_votes_for("agent_1") == 0
        assert result.get_votes_for("agent_2") == 2
        assert result.get_votes_for("agent_3") == 1
    
    def test_aggregate_with_zero_votes(self) -> None:
        """Test that agents with zero votes are included."""
        votes = [
            Vote("agent_1", "agent_2", 1),
        ]
        
        result = aggregate_votes(
            votes,
            1,
            ["agent_1", "agent_2", "agent_3", "agent_4"]
        )
        
        assert len(result.results) == 4
        assert result.get_votes_for("agent_1") == 0
        assert result.get_votes_for("agent_2") == 1
        assert result.get_votes_for("agent_3") == 0
        assert result.get_votes_for("agent_4") == 0
    
    def test_aggregate_empty_votes(self) -> None:
        """Test aggregating with no votes cast."""
        result = aggregate_votes([], 1, ["agent_1", "agent_2"])
        
        assert len(result.votes) == 0
        assert len(result.results) == 2
        assert result.get_votes_for("agent_1") == 0
        assert result.get_votes_for("agent_2") == 0
    
    def test_aggregate_all_vote_for_one(self) -> None:
        """Test when all agents vote for the same target."""
        votes = [
            Vote("agent_1", "agent_4", 1),
            Vote("agent_2", "agent_4", 1),
            Vote("agent_3", "agent_4", 1),
        ]
        
        result = aggregate_votes(
            votes,
            1,
            ["agent_1", "agent_2", "agent_3", "agent_4"]
        )
        
        assert result.get_votes_for("agent_4") == 3
        assert result.get_votes_for("agent_1") == 0
        assert result.get_votes_for("agent_2") == 0
        assert result.get_votes_for("agent_3") == 0
    
    def test_results_are_sorted(self) -> None:
        """Test that results are sorted by agent_id."""
        votes = [
            Vote("agent_3", "agent_1", 1),
            Vote("agent_1", "agent_2", 1),
        ]
        
        result = aggregate_votes(votes, 1, ["agent_3", "agent_1", "agent_2"])
        
        # Results should be sorted alphabetically
        agent_ids = [r.agent_id for r in result.results]
        assert agent_ids == sorted(agent_ids)
