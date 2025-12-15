"""Agent registry for managing active agents in the arena.

The registry provides a central place to track and access all agents.
It enforces unique agent IDs and provides lookup functionality.
"""

from typing import Iterator

from ai_hunger_games.agents.agent import Agent
from ai_hunger_games.core.logging_setup import get_logger


logger = get_logger(__name__)


class AgentNotFoundError(Exception):
    """Raised when an agent is not found in the registry."""
    
    pass


class DuplicateAgentError(Exception):
    """Raised when attempting to register an agent with a duplicate ID."""
    
    pass


class AgentRegistry:
    """Registry for managing active agents in the arena.
    
    Provides registration, lookup, and iteration over agents.
    Enforces unique agent IDs across the registry.
    """
    
    def __init__(self) -> None:
        """Initialize an empty agent registry."""
        self._agents: dict[str, Agent] = {}
    
    def register(self, agent: Agent) -> None:
        """Register a new agent in the registry.
        
        Args:
            agent: The agent to register.
        
        Raises:
            DuplicateAgentError: If an agent with the same ID exists.
        """
        if agent.agent_id in self._agents:
            raise DuplicateAgentError(
                f"Agent with ID '{agent.agent_id}' already registered"
            )
        
        self._agents[agent.agent_id] = agent
        logger.info(f"Registered agent '{agent.agent_id}' in registry")
    
    def get(self, agent_id: str) -> Agent:
        """Get an agent by ID.
        
        Args:
            agent_id: The unique identifier of the agent.
        
        Returns:
            The agent with the given ID.
        
        Raises:
            AgentNotFoundError: If no agent with that ID exists.
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found")
        
        return self._agents[agent_id]
    
    def get_all(self) -> list[Agent]:
        """Get all registered agents.
        
        Returns:
            List of all agents in registration order.
        """
        return list(self._agents.values())
    
    def get_ids(self) -> list[str]:
        """Get all registered agent IDs.
        
        Returns:
            List of agent IDs in registration order.
        """
        return list(self._agents.keys())
    
    def count(self) -> int:
        """Get the number of registered agents.
        
        Returns:
            Number of agents in the registry.
        """
        return len(self._agents)
    
    def remove(self, agent_id: str) -> Agent:
        """Remove an agent from the registry.
        
        Args:
            agent_id: The ID of the agent to remove.
        
        Returns:
            The removed agent.
        
        Raises:
            AgentNotFoundError: If no agent with that ID exists.
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found")
        
        agent = self._agents.pop(agent_id)
        logger.info(f"Removed agent '{agent_id}' from registry")
        return agent
    
    def clear(self) -> None:
        """Remove all agents from the registry."""
        count = len(self._agents)
        self._agents.clear()
        logger.info(f"Cleared {count} agents from registry")
    
    def __iter__(self) -> Iterator[Agent]:
        """Iterate over all agents in the registry."""
        return iter(self._agents.values())
    
    def __contains__(self, agent_id: str) -> bool:
        """Check if an agent ID is in the registry."""
        return agent_id in self._agents
