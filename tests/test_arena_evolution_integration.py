"""Tests for ArenaController evolution integration."""

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
from ai_hunger_games.arena.elimination import EliminationResult
from ai_hunger_games.core.config import Settings
from ai_hunger_games.evolution.personality_generator import PersonalityGenerator
from ai_hunger_games.evolution.replacement import AgentReplacementCoordinator


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


class TestArenaControllerReplacement:
    """Tests for ArenaController evolution integration."""
    
    def test_execute_replacement_without_coordinator(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test that replacement does nothing without coordinator."""
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings
            # No replacement_coordinator
        )
        
        elimination_result = EliminationResult(
            eliminated_agent_id="agent_1",
            cumulative_votes=10,
            was_tie=False
        )
        
        # Should not raise, just log warning
        controller.execute_replacement(elimination_result)
        
        # Agent should still be in registry
        assert "agent_1" in populated_registry
    
    def test_execute_replacement_with_coordinator(
        self,
        populated_registry: AgentRegistry,
        sample_settings: Settings
    ) -> None:
        """Test executing replacement with coordinator."""
        generator = PersonalityGenerator(base_seed=sample_settings.random_seed)
        coordinator = AgentReplacementCoordinator(
            registry=populated_registry,
            generator=generator,
            memory_window=sample_settings.memory_window
        )
        
        controller = ArenaController(
            registry=populated_registry,
            settings=sample_settings,
            replacement_coordinator=coordinator
        )
        
        # Run a round
        controller.start_round("Test prompt")
        
        old_agent = populated_registry.get("agent_1")
        old_personality = old_agent.personality
        
        elimination_result = EliminationResult(
            eliminated_agent_id="agent_1",
            cumulative_votes=10,
            was_tie=False
        )
        
        controller.execute_replacement(elimination_result)
        
        # Agent should still exist but with new personality
        new_agent = populated_registry.get("agent_1")
        assert new_agent.personality != old_personality
        
        # Post-mortem should be recorded
        records = coordinator.get_post_mortem_records()
        assert len(records) == 1
        assert records[0].agent_id == "agent_1"
    
    def test_full_cycle_with_replacement(
        self,
        sample_personality: Personality,
        sample_settings: Settings
    ) -> None:
        """Test full cycle: round, voting, elimination, replacement."""
        registry = AgentRegistry()
        
        for i in range(4):
            agent = Agent(
                agent_id=f"agent_{i}",
                personality=sample_personality
            )
            registry.register(agent)
        
        generator = PersonalityGenerator(base_seed=sample_settings.random_seed)
        coordinator = AgentReplacementCoordinator(
            registry=registry,
            generator=generator
        )
        
        controller = ArenaController(
            registry=registry,
            settings=sample_settings,
            replacement_coordinator=coordinator
        )
        
        # Round 1
        round1 = controller.start_round("Prompt 1")
        controller.conduct_voting(round1, {
            "agent_0": "agent_1",
            "agent_1": "agent_2",
            "agent_2": "agent_1",
            "agent_3": "agent_1",
        })
        
        # Determine elimination
        elimination_result = controller.determine_elimination_candidate()
        assert elimination_result.eliminated_agent_id == "agent_1"
        
        # Execute replacement
        controller.execute_replacement(elimination_result)
        
        # Registry should still have 4 agents
        assert registry.count() == 4
        
        # agent_1 should still exist but be different
        new_agent_1 = registry.get("agent_1")
        assert new_agent_1.personality != sample_personality
        
        # Post-mortem records
        records = coordinator.get_post_mortem_records()
        assert len(records) == 1
