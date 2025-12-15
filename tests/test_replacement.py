"""Tests for agent replacement module."""

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
from ai_hunger_games.evolution.personality_generator import PersonalityGenerator
from ai_hunger_games.evolution.replacement import AgentReplacementCoordinator


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
def registry_with_agent(sample_personality: Personality) -> AgentRegistry:
    """Create a registry with one agent."""
    registry = AgentRegistry()
    agent = Agent(
        agent_id="agent_1",
        personality=sample_personality
    )
    registry.register(agent)
    return registry


@pytest.fixture
def generator() -> PersonalityGenerator:
    """Create a personality generator."""
    return PersonalityGenerator(base_seed=42)


class TestAgentReplacementCoordinator:
    """Tests for AgentReplacementCoordinator class."""
    
    def test_replace_agent(
        self,
        registry_with_agent: AgentRegistry,
        generator: PersonalityGenerator
    ) -> None:
        """Test replacing an agent."""
        coordinator = AgentReplacementCoordinator(
            registry=registry_with_agent,
            generator=generator
        )
        
        old_agent = registry_with_agent.get("agent_1")
        old_personality = old_agent.personality
        
        new_agent = coordinator.replace_agent(
            eliminated_agent_id="agent_1",
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=False
        )
        
        # New agent should have different personality
        assert new_agent.agent_id == "agent_1"
        assert new_agent.personality != old_personality
        
        # Registry should contain the new agent
        current_agent = registry_with_agent.get("agent_1")
        assert current_agent is new_agent
    
    def test_post_mortem_record_created(
        self,
        registry_with_agent: AgentRegistry,
        generator: PersonalityGenerator
    ) -> None:
        """Test that post-mortem record is created on replacement."""
        coordinator = AgentReplacementCoordinator(
            registry=registry_with_agent,
            generator=generator
        )
        
        coordinator.replace_agent(
            eliminated_agent_id="agent_1",
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=False
        )
        
        records = coordinator.get_post_mortem_records()
        
        assert len(records) == 1
        assert records[0].agent_id == "agent_1"
        assert records[0].rounds_survived == 5
        assert records[0].total_votes_received == 10
        assert records[0].elimination_round == 5
        assert records[0].was_tie is False
    
    def test_multiple_replacements(
        self,
        sample_personality: Personality,
        generator: PersonalityGenerator
    ) -> None:
        """Test multiple agent replacements."""
        registry = AgentRegistry()
        
        for i in range(3):
            agent = Agent(
                agent_id=f"agent_{i}",
                personality=sample_personality
            )
            registry.register(agent)
        
        coordinator = AgentReplacementCoordinator(
            registry=registry,
            generator=generator
        )
        
        # Replace agent_0
        coordinator.replace_agent(
            eliminated_agent_id="agent_0",
            rounds_survived=2,
            total_votes_received=5,
            elimination_round=2,
            was_tie=False
        )
        
        # Replace agent_1
        coordinator.replace_agent(
            eliminated_agent_id="agent_1",
            rounds_survived=4,
            total_votes_received=8,
            elimination_round=4,
            was_tie=True
        )
        
        records = coordinator.get_post_mortem_records()
        
        assert len(records) == 2
        assert records[0].agent_id == "agent_0"
        assert records[1].agent_id == "agent_1"
        
        # All original agents should still exist (with new personalities)
        assert registry.count() == 3
    
    def test_replacement_memory_window(
        self,
        registry_with_agent: AgentRegistry,
        generator: PersonalityGenerator
    ) -> None:
        """Test that replacement respects memory window."""
        coordinator = AgentReplacementCoordinator(
            registry=registry_with_agent,
            generator=generator,
            memory_window=10
        )
        
        new_agent = coordinator.replace_agent(
            eliminated_agent_id="agent_1",
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=False
        )
        
        assert new_agent.memory.window_size == 10
    
    def test_get_post_mortem_records_returns_copy(
        self,
        registry_with_agent: AgentRegistry,
        generator: PersonalityGenerator
    ) -> None:
        """Test that getting records returns a copy."""
        coordinator = AgentReplacementCoordinator(
            registry=registry_with_agent,
            generator=generator
        )
        
        coordinator.replace_agent(
            eliminated_agent_id="agent_1",
            rounds_survived=5,
            total_votes_received=10,
            elimination_round=5,
            was_tie=False
        )
        
        records1 = coordinator.get_post_mortem_records()
        records2 = coordinator.get_post_mortem_records()
        
        # Should be different list objects
        assert records1 is not records2
        # But same content
        assert len(records1) == len(records2)
