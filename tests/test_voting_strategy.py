"""Tests for voting strategy module."""

import pytest

from ai_hunger_games.arena.round_state import RoundState
from ai_hunger_games.voting.strategy import (
    InvalidVoteError,
    SelfVoteError,
    collect_votes,
)


class TestCollectVotes:
    """Tests for collect_votes function."""
    
    def test_collect_valid_votes(self) -> None:
        """Test collecting valid votes."""
        round_state = RoundState(round_number=1, prompt="Test")
        round_state.add_response("agent_1", "Response 1")
        round_state.add_response("agent_2", "Response 2")
        round_state.add_response("agent_3", "Response 3")
        
        vote_choices = {
            "agent_1": "agent_2",
            "agent_2": "agent_3",
            "agent_3": "agent_1",
        }
        
        votes = collect_votes(round_state, vote_choices)
        
        assert len(votes) == 3
        assert votes[0].voter_id == "agent_1"
        assert votes[0].voted_for_id == "agent_2"
        assert votes[1].voter_id == "agent_2"
        assert votes[1].voted_for_id == "agent_3"
    
    def test_self_vote_raises_error(self) -> None:
        """Test that self-voting raises SelfVoteError."""
        round_state = RoundState(round_number=1, prompt="Test")
        round_state.add_response("agent_1", "Response 1")
        round_state.add_response("agent_2", "Response 2")
        
        vote_choices = {
            "agent_1": "agent_1",  # Self-vote
            "agent_2": "agent_1",
        }
        
        with pytest.raises(SelfVoteError, match="cannot vote for itself"):
            collect_votes(round_state, vote_choices)
    
    def test_invalid_vote_target_raises_error(self) -> None:
        """Test that voting for non-existent agent raises error."""
        round_state = RoundState(round_number=1, prompt="Test")
        round_state.add_response("agent_1", "Response 1")
        round_state.add_response("agent_2", "Response 2")
        
        vote_choices = {
            "agent_1": "agent_999",  # Non-existent agent
            "agent_2": "agent_1",
        }
        
        with pytest.raises(InvalidVoteError, match="not found in round"):
            collect_votes(round_state, vote_choices)
    
    def test_empty_votes(self) -> None:
        """Test collecting zero votes."""
        round_state = RoundState(round_number=1, prompt="Test")
        round_state.add_response("agent_1", "Response 1")
        
        votes = collect_votes(round_state, {})
        
        assert len(votes) == 0
