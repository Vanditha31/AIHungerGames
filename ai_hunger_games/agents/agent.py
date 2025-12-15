"""Agent abstraction for AI Hunger Games.

Agents are stateless models + stateful wrappers. The Agent class
manages personality, memory, and response generation interface.
Actual LLM calls are deferred to Phase 1+ implementation.
"""

from dataclasses import dataclass
from typing import Optional

from ai_hunger_games.agents.memory import AgentMemory, MemoryEntry
from ai_hunger_games.agents.personality import Personality
from ai_hunger_games.core.logging_setup import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class RoundContext:
    """Context provided to agent for response generation.
    
    Contains information about the current round that the agent
    is allowed to see when generating a response.
    """
    
    round_number: int
    prompt: str


class Agent:
    """Represents a single agent in the arena.
    
    Each agent has a unique ID, personality traits, and memory.
    The agent generates responses based on personality and context.
    Per ARCHITECTURE.md, agents never know other agents' identities.
    """
    
    def __init__(
        self,
        agent_id: str,
        personality: Personality,
        memory_window: int = 5
    ) -> None:
        """Initialize an agent with personality and memory.
        
        Args:
            agent_id: Unique identifier for this agent.
            personality: The agent's personality traits.
            memory_window: Number of rounds to keep in memory.
        """
        if not agent_id:
            raise ValueError("Agent ID cannot be empty")
        
        self._agent_id = agent_id
        self._personality = personality
        self._memory = AgentMemory(window_size=memory_window)
        
        logger.info(
            f"Created agent '{agent_id}' with personality: "
            f"{personality.describe()}"
        )
    
    @property
    def agent_id(self) -> str:
        """Get the agent's unique identifier."""
        return self._agent_id
    
    @property
    def personality(self) -> Personality:
        """Get the agent's personality (read-only)."""
        return self._personality
    
    @property
    def memory(self) -> AgentMemory:
        """Get the agent's memory (read-only access to entries)."""
        return self._memory
    
    def generate_response(self, context: RoundContext) -> str:
        """Generate a response to the given prompt.
        
        Phase 1: Returns a placeholder response.
        Future phases will integrate with Ollama for actual LLM calls.
        
        Args:
            context: The round context with prompt and metadata.
        
        Returns:
            The agent's response to the prompt.
        """
        logger.debug(
            f"Agent '{self._agent_id}' generating response for round "
            f"{context.round_number}"
        )
        
        response = self._generate_stub_response(context)
        
        entry = MemoryEntry(
            round_number=context.round_number,
            prompt=context.prompt,
            response=response,
        )
        self._memory.add_entry(entry)
        
        return response
    
    def _generate_stub_response(self, context: RoundContext) -> str:
        """Generate a stub response for Phase 1 testing.
        
        This will be replaced with actual LLM calls in later phases.
        
        Args:
            context: The round context.
        
        Returns:
            A placeholder response string.
        """
        return (
            f"[Agent {self._agent_id}] Response to round {context.round_number}: "
            f"'{context.prompt[:50]}...' "
            f"(Personality: {self._personality.communication_style.value})"
        )
