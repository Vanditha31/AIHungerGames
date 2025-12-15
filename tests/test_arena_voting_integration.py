"""Tests for ArenaController voting and elimination integration."""

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
from ai_hunger_games.arena.controller import ArenaController
from ai_hunger_games.core.config import Settings
from ai_hunger_games.voting.strategy import SelfVoteError


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


class TestArenaControllerVoting:
    """Tests for ArenaController voting integration."""
    
    def test_conduct_voting(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test conducting a voting round."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        round_state = controller.start_round("Test prompt")
        
        vote_choices = {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_3",
            "agent_3": "agent_0",
        }
        
        result = controller.conduct_voting(round_state, vote_choices)
        
        assert result.round_number == 1
        assert len(result.votes) == 4
        assert result.get_votes_for("agent_0") == 1
        assert result.get_votes_for("agent_1") == 1
        assert result.get_votes_for("agent_2") == 1
        assert result.get_votes_for("agent_3") == 1
    
    def test_conduct_voting_validates_self_vote(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that self-voting is caught during voting."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        round_state = controller.start_round("Test prompt")
        
        vote_choices = {
            "agent_0": "agent_0",  # Self-vote
            "agent_1": "agent_2",
        }
        
        with pytest.raises(SelfVoteError):
            controller.conduct_voting(round_state, vote_choices)
    
    def test_cumulative_votes_tracking(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that cumulative votes are tracked across rounds."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        # Round 1: give agent_1 3 votes
        round1 = controller.start_round("Prompt 1")
        controller.conduct_voting(round1, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_1",
            "agent_3": "agent_1",
        })
        
        # Round 2
        round2 = controller.start_round("Prompt 2")
        controller.conduct_voting(round2, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_1",
            "agent_3": "agent_1",
        })
        
        # agent_1 should have 6 cumulative votes (3 + 3)
        assert controller._cumulative_votes["agent_1"] == 6
        assert controller._cumulative_votes["agent_2"] == 2  # 1 per round
        assert controller._cumulative_votes["agent_0"] == 0


class TestArenaControllerElimination:
    """Tests for ArenaController elimination integration."""
    
    def test_determine_elimination_candidate(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test determining elimination candidate."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        round_state = controller.start_round("Test prompt")
        controller.conduct_voting(round_state, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_1",
            "agent_3": "agent_1",
        })
        
        result = controller.determine_elimination_candidate()
        
        # agent_1 has 3 votes, highest
        assert result.eliminated_agent_id == "agent_1"
        assert result.cumulative_votes == 3
    
    def test_elimination_without_voting_raises(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that elimination without voting raises error."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        controller.start_round("Test prompt")
        
        with pytest.raises(ValueError, match="without voting history"):
            controller.determine_elimination_candidate()
    
    def test_elimination_with_tie_breaking(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test elimination when agents are tied."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        # Round 1: agent_1 and agent_2 each get 1 vote
        round1 = controller.start_round("Prompt 1")
        controller.conduct_voting(round1, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_3",
            "agent_3": "agent_0",
        })
        
        # Round 2: give only agent_0 an extra vote (now at 3 total)
        round2 = controller.start_round("Prompt 2")
        controller.conduct_voting(round2, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_0",
            "agent_3": "agent_0",
        })
        
        result = controller.determine_elimination_candidate()
        
        # agent_0 now has 3 votes (1 + 2), highest
        assert result.eliminated_agent_id == "agent_0"
        assert result.cumulative_votes == 3
        assert result.was_tie is False
    
    def test_historical_average_calculation(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that historical average is calculated correctly."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
        )
        
        # Round 1: agent_1 gets 3 votes
        round1 = controller.start_round("Prompt 1")
        controller.conduct_voting(round1, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_1",
            "agent_3": "agent_1",
        })
        
        # Round 2
        round2 = controller.start_round("Prompt 2")
        controller.conduct_voting(round2, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_0",
            "agent_3": "agent_0",
        })
        
        # agent_1: 3 votes in round 1, 1 in round 2 = avg 2.0
        avg_agent_1 = controller._calculate_historical_average("agent_1")
        assert avg_agent_1 == 2.0
        
        # agent_0: 0 votes in round 1, 2 in round 2 = avg 1.0
        avg_agent_0 = controller._calculate_historical_average("agent_0")
        assert avg_agent_0 == 1.0
