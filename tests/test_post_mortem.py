"""Tests for post-mortem module."""

import pytest

from ai_hunger_games.agents.personality import (
    CommunicationStyle,
    EthicalStance,
    Personality,
    RiskTolerance,
    SocialStrategy,
)
from ai_hunger_games.evolution.post_mortem import PostMortemRecord


@pytest.fixture
def sample_personality() -> Personality:
    """Create a sample personality for testing."""
    return Personality(
        communication_style=CommunicationStyle.CONCISE,
        ethical_stance=EthicalStance.STRICT,
        social_strategy=SocialStrategy.COOPERATIVE,
        risk_tolerance=RiskTolerance.LOW,
        seed=42
    )


class TestPostMortemRecord:
    """Tests for PostMortemRecord dataclass."""
    
    def test_create_post_mortem(self, sample_personality: Personality) -> None:
        """Test creating a post-mortem record."""
        record = PostMortemRecord(
            agent_id="agent_1",
            personality=sample_personality,
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=False
        )
        
        assert record.agent_id == "agent_1"
        assert record.personality == sample_personality
        assert record.rounds_survived == 5
        assert record.total_votes_received == 10
        assert record.elimination_round == 5
        assert record.was_tie is False
    
    def test_post_mortem_is_frozen(self, sample_personality: Personality) -> None:
        """Test that post-mortem record cannot be modified."""
        record = PostMortemRecord(
            agent_id="agent_1",
            personality=sample_personality,
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=False
        )
        
        with pytest.raises(AttributeError):
            record.rounds_survived = 10
    
    def test_to_dict(self, sample_personality: Personality) -> None:
        """Test converting post-mortem to dictionary."""
        record = PostMortemRecord(
            agent_id="agent_1",
            personality=sample_personality,
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=True
        )
        
        result = record.to_dict()
        
        assert result["agent_id"] == "agent_1"
        assert result["rounds_survived"] == 5
        assert result["total_votes_received"] == 10
        assert result["elimination_round"] == 5
        assert result["was_tie"] is True
        assert "personality" in result
        assert isinstance(result["personality"], dict)
    
    def test_personality_in_dict(self, sample_personality: Personality) -> None:
        """Test that personality is properly serialized in dict."""
        record = PostMortemRecord(
            agent_id="agent_1",
            personality=sample_personality,
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=False
        )
        
        result = record.to_dict()
        personality_dict = result["personality"]
        
        assert personality_dict["communication_style"] == "concise"
        assert personality_dict["ethical_stance"] == "strict"
        assert personality_dict["social_strategy"] == "cooperative"
        assert personality_dict["risk_tolerance"] == "low"
