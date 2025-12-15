"""Tests for agent module."""

import pytest

from ai_hunger_games.agents.agent import Agent, RoundContext
from ai_hunger_games.agents.personality import (
    CommunicationStyle,
    EthicalStance,
    Personality,
    RiskTolerance,
    SocialStrategy,
)


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


class TestAgent:
    """Tests for Agent class."""
    
    def test_create_agent(self, sample_personality: Personality) -> None:
        """Test creating a valid agent."""
        agent = Agent(
            agent_id="agent_1",
            personality=sample_personality
        )
        
        assert agent.agent_id == "agent_1"
        assert agent.personality == sample_personality
        assert agent.memory.count() == 0
    
    def test_create_agent_with_custom_memory(
        self, sample_personality: Personality
    ) -> None:
        """Test creating agent with custom memory window."""
        agent = Agent(
            agent_id="agent_1",
            personality=sample_personality,
            memory_window=10
        )
        
        assert agent.memory.window_size == 10
    
    def test_empty_agent_id_raises(self, sample_personality: Personality) -> None:
        """Test that empty agent ID raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Agent(agent_id="", personality=sample_personality)
    
    def test_generate_response(self, sample_personality: Personality) -> None:
        """Test generating a stub response."""
        agent = Agent(
            agent_id="agent_1",
            personality=sample_personality
        )
        
        context = RoundContext(round_number=1, prompt="What is 2+2?")
        response = agent.generate_response(context)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "agent_1" in response
    
    def test_response_adds_to_memory(
        self, sample_personality: Personality
    ) -> None:
        """Test that generating response adds entry to memory."""
        agent = Agent(
            agent_id="agent_1",
            personality=sample_personality
        )
        
        assert agent.memory.count() == 0
        
        context = RoundContext(round_number=1, prompt="Test prompt")
        agent.generate_response(context)
        
        assert agent.memory.count() == 1
        
        entry = agent.memory.get_latest()
        assert entry.round_number == 1
        assert entry.prompt == "Test prompt"
    
    def test_multiple_responses(self, sample_personality: Personality) -> None:
        """Test generating multiple responses adds to memory."""
        agent = Agent(
            agent_id="agent_1",
            personality=sample_personality,
            memory_window=5
        )
        
        for i in range(3):
            context = RoundContext(round_number=i + 1, prompt=f"Prompt {i}")
            agent.generate_response(context)
        
        assert agent.memory.count() == 3
        entries = agent.memory.get_entries()
        assert entries[0].round_number == 1
        assert entries[2].round_number == 3


class TestRoundContext:
    """Tests for RoundContext dataclass."""
    
    def test_create_context(self) -> None:
        """Test creating a round context."""
        context = RoundContext(round_number=5, prompt="Test prompt")
        
        assert context.round_number == 5
        assert context.prompt == "Test prompt"
    
    def test_context_is_frozen(self) -> None:
        """Test that context cannot be modified."""
        context = RoundContext(round_number=1, prompt="Test")
        
        with pytest.raises(AttributeError):
            context.round_number = 2
