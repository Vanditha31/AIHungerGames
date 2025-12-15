"""Tests for voting types module."""

import pytest

from ai_hunger_games.voting.types import Vote, VoteResult, VotingRoundResult


class TestVote:
    """Tests for Vote dataclass."""
    
    def test_create_vote(self) -> None:
        """Test creating a vote."""
        vote = Vote(
            voter_id="agent_1",
            voted_for_id="agent_2",
            round_number=1
        )
        
        assert vote.voter_id == "agent_1"
        assert vote.voted_for_id == "agent_2"
        assert vote.round_number == 1
    
    def test_vote_is_frozen(self) -> None:
        """Test that votes cannot be modified."""
        vote = Vote(
            voter_id="agent_1",
            voted_for_id="agent_2",
            round_number=1
        )
        
        with pytest.raises(AttributeError):
            vote.voter_id = "agent_3"


class TestVoteResult:
    """Tests for VoteResult dataclass."""
    
    def test_create_vote_result(self) -> None:
        """Test creating a vote result."""
        result = VoteResult(agent_id="agent_1", votes_received=3)
        
        assert result.agent_id == "agent_1"
        assert result.votes_received == 3
    
    def test_vote_result_is_frozen(self) -> None:
        """Test that vote results cannot be modified."""
        result = VoteResult(agent_id="agent_1", votes_received=3)
        
        with pytest.raises(AttributeError):
            result.votes_received = 5


class TestVotingRoundResult:
    """Tests for VotingRoundResult dataclass."""
    
    def test_create_voting_round_result(self) -> None:
        """Test creating a voting round result."""
        votes = (
            Vote("agent_1", "agent_2", 1),
            Vote("agent_2", "agent_3", 1),
        )
        results = (
            VoteResult("agent_1", 0),
            VoteResult("agent_2", 1),
            VoteResult("agent_3", 1),
        )
        
        round_result = VotingRoundResult(
            round_number=1,
            votes=votes,
            results=results
        )
        
        assert round_result.round_number == 1
        assert len(round_result.votes) == 2
        assert len(round_result.results) == 3
    
    def test_get_votes_for(self) -> None:
        """Test getting votes for a specific agent."""
        results = (
            VoteResult("agent_1", 0),
            VoteResult("agent_2", 3),
            VoteResult("agent_3", 1),
        )
        
        round_result = VotingRoundResult(
            round_number=1,
            votes=(),
            results=results
        )
        
        assert round_result.get_votes_for("agent_1") == 0
        assert round_result.get_votes_for("agent_2") == 3
        assert round_result.get_votes_for("agent_3") == 1
    
    def test_get_votes_for_nonexistent(self) -> None:
        """Test getting votes for non-existent agent returns 0."""
        results = (VoteResult("agent_1", 2),)
        
        round_result = VotingRoundResult(
            round_number=1,
            votes=(),
            results=results
        )
        
        assert round_result.get_votes_for("agent_999") == 0
