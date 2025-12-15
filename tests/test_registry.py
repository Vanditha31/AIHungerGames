"""Tests for agent registry module."""

import pytest

from ai_hunger_games.agents.agent import Agent
from ai_hunger_games.agents.personality import (
    CommunicationStyle,
    EthicalStance,
    Personality,
    RiskTolerance,
    SocialStrategy,
)
from ai_hunger_games.agents.registry import (
    AgentNotFoundError,
    AgentRegistry,
    DuplicateAgentError,
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
def sample_agent(sample_personality: Personality) -> Agent:
    """Create a sample agent for testing."""
    return Agent(agent_id="agent_1", personality=sample_personality)


class TestAgentRegistry:
    """Tests for AgentRegistry class."""
    
    def test_create_empty_registry(self) -> None:
        """Test creating an empty registry."""
        registry = AgentRegistry()
        
        assert registry.count() == 0
        assert registry.get_all() == []
    
    def test_register_agent(self, sample_agent: Agent) -> None:
        """Test registering an agent."""
        registry = AgentRegistry()
        registry.register(sample_agent)
        
        assert registry.count() == 1
        assert "agent_1" in registry
    
    def test_register_duplicate_raises(
        self, sample_personality: Personality
    ) -> None:
        """Test that registering duplicate ID raises error."""
        registry = AgentRegistry()
        
        agent1 = Agent(agent_id="agent_1", personality=sample_personality)
        agent2 = Agent(agent_id="agent_1", personality=sample_personality)
        
        registry.register(agent1)
        
        with pytest.raises(DuplicateAgentError):
            registry.register(agent2)
    
    def test_get_agent(self, sample_agent: Agent) -> None:
        """Test getting an agent by ID."""
        registry = AgentRegistry()
        registry.register(sample_agent)
        
        retrieved = registry.get("agent_1")
        
        assert retrieved is sample_agent
    
    def test_get_nonexistent_raises(self) -> None:
        """Test that getting nonexistent agent raises error."""
        registry = AgentRegistry()
        
        with pytest.raises(AgentNotFoundError):
            registry.get("nonexistent")
    
    def test_get_all(self, sample_personality: Personality) -> None:
        """Test getting all agents."""
        registry = AgentRegistry()
        
        agents = [
            Agent(agent_id=f"agent_{i}", personality=sample_personality)
            for i in range(3)
        ]
        
        for agent in agents:
            registry.register(agent)
        
        all_agents = registry.get_all()
        
        assert len(all_agents) == 3
        assert all_agents[0].agent_id == "agent_0"
    
    def test_get_ids(self, sample_personality: Personality) -> None:
        """Test getting all agent IDs."""
        registry = AgentRegistry()
        
        for i in range(3):
            agent = Agent(agent_id=f"agent_{i}", personality=sample_personality)
            registry.register(agent)
        
        ids = registry.get_ids()
        
        assert ids == ["agent_0", "agent_1", "agent_2"]
    
    def test_remove_agent(self, sample_agent: Agent) -> None:
        """Test removing an agent."""
        registry = AgentRegistry()
        registry.register(sample_agent)
        
        removed = registry.remove("agent_1")
        
        assert removed is sample_agent
        assert registry.count() == 0
        assert "agent_1" not in registry
    
    def test_remove_nonexistent_raises(self) -> None:
        """Test that removing nonexistent agent raises error."""
        registry = AgentRegistry()
        
        with pytest.raises(AgentNotFoundError):
            registry.remove("nonexistent")
    
    def test_clear(self, sample_personality: Personality) -> None:
        """Test clearing all agents."""
        registry = AgentRegistry()
        
        for i in range(3):
            agent = Agent(agent_id=f"agent_{i}", personality=sample_personality)
            registry.register(agent)
        
        registry.clear()
        
        assert registry.count() == 0
    
    def test_iteration(self, sample_personality: Personality) -> None:
        """Test iterating over registry."""
        registry = AgentRegistry()
        
        for i in range(3):
            agent = Agent(agent_id=f"agent_{i}", personality=sample_personality)
            registry.register(agent)
        
        agent_ids = [agent.agent_id for agent in registry]
        
        assert agent_ids == ["agent_0", "agent_1", "agent_2"]
    
    def test_contains(self, sample_agent: Agent) -> None:
        """Test checking if agent exists."""
        registry = AgentRegistry()
        
        assert "agent_1" not in registry
        
        registry.register(sample_agent)
        
        assert "agent_1" in registry
        assert "agent_2" not in registry
