"""Tests for arena controller module."""

from pathlib import Path

import pytest

from ai_hunger_games.agents.agent import Agent
from ai_hunger_games.agents.personality import (
    CommunicationStyle,
    EthicalStance,
    Personality,
    RiskTolerance,
    SocialStrategy,
)
from ai_hunger_games.agents.registry import AgentRegistry
from ai_hunger_games.arena.controller import ArenaController, InsufficientAgentsError
from ai_hunger_games.arena.round_state import RoundState
from ai_hunger_games.core.config import Settings


@pytest.fixture
def sample_settings() -> Settings:
    """Create sample settings for testing."""
    return Settings(
        model_name="llama3.1:8b",
        temperature=0.2,
        ollama_base_url="http://localhost:11434",
        num_agents=8,
        rounds_per_elimination=2,
        memory_window=5,
        random_seed=42,
        log_level="INFO",
        log_file="logs/test.log"
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


@pytest.fixture
def populated_registry(sample_personality: Personality) -> AgentRegistry:
    """Create a registry with 4 agents."""
    registry = AgentRegistry()
    
    for i in range(4):
        agent = Agent(
            agent_id=f"agent_{i}",
            personality=sample_personality
        )
        registry.register(agent)
    
    return registry


class TestArenaController:
    """Tests for ArenaController class."""
    
    def test_create_controller(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test creating an arena controller."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        assert controller.current_round == 0
        assert controller.agent_count == 4
    
    def test_start_round(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test starting a round."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        round_state = controller.start_round("What is 2+2?")
        
        assert round_state.round_number == 1
        assert round_state.prompt == "What is 2+2?"
        assert round_state.is_complete is True
        assert round_state.response_count() == 4
    
    def test_round_collects_all_responses(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that round collects response from each agent."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        round_state = controller.start_round("Test prompt")
        
        for i in range(4):
            response = round_state.get_response(f"agent_{i}")
            assert response is not None
            assert len(response) > 0
    
    def test_current_round_increments(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that current round increments with each round."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        assert controller.current_round == 0
        
        controller.start_round("Round 1")
        assert controller.current_round == 1
        
        controller.start_round("Round 2")
        assert controller.current_round == 2
    
    def test_round_history(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that round history is maintained."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        controller.start_round("First prompt")
        controller.start_round("Second prompt")
        
        history = controller.get_round_history()
        
        assert len(history) == 2
        assert history[0].prompt == "First prompt"
        assert history[1].prompt == "Second prompt"
    
    def test_get_round(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test getting a specific round."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        controller.start_round("First")
        controller.start_round("Second")
        
        round1 = controller.get_round(1)
        assert round1.prompt == "First"
        
        round2 = controller.get_round(2)
        assert round2.prompt == "Second"
        
        assert controller.get_round(3) is None
    
    def test_insufficient_agents_raises(
        self,
        sample_personality: Personality,
        sample_settings: Settings
    ) -> None:
        """Test that too few agents raises error."""
        registry = AgentRegistry()
        
        for i in range(2):
            agent = Agent(
                agent_id=f"agent_{i}",
                personality=sample_personality
            )
            registry.register(agent)
        
        controller = ArenaController(
            registry=registry,
            settings=sample_settings
        )
        
        with pytest.raises(InsufficientAgentsError, match="at least 3"):
            controller.start_round("Test prompt")


class TestRoundState:
    """Tests for RoundState class."""
    
    def test_create_round_state(self) -> None:
        """Test creating a round state."""
        state = RoundState(round_number=1, prompt="Test")
        
        assert state.round_number == 1
        assert state.prompt == "Test"
        assert state.responses == []
        assert state.is_complete is False
    
    def test_add_response(self) -> None:
        """Test adding responses."""
        state = RoundState(round_number=1, prompt="Test")
        
        state.add_response("agent_1", "Response 1")
        state.add_response("agent_2", "Response 2")
        
        assert state.response_count() == 2
    
    def test_get_response(self) -> None:
        """Test getting a specific agent's response."""
        state = RoundState(round_number=1, prompt="Test")
        
        state.add_response("agent_1", "Response 1")
        state.add_response("agent_2", "Response 2")
        
        assert state.get_response("agent_1") == "Response 1"
        assert state.get_response("agent_2") == "Response 2"
        assert state.get_response("agent_3") is None
