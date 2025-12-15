"""Round state management for the arena.

Contains data structures representing round state and agent responses.
These are shared between the arena controller and other modules.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentResponse:
    """A single agent's response in a round.
    
    Represents the output from one agent for a given prompt.
    """
    
    agent_id: str
    response: str


@dataclass
class RoundState:
    """State of a single round in the arena.
    
    Tracks the prompt, all responses, and completion status.
    This is a mutable dataclass as state evolves during the round.
    """
    
    round_number: int
    prompt: str
    responses: list[AgentResponse] = field(default_factory=list)
    is_complete: bool = False
    
    def add_response(self, agent_id: str, response: str) -> None:
        """Add an agent's response to this round.
        
        Args:
            agent_id: The responding agent's ID.
            response: The agent's response text.
        """
        self.responses.append(AgentResponse(agent_id=agent_id, response=response))
    
    def get_response(self, agent_id: str) -> str | None:
        """Get a specific agent's response.
        
        Args:
            agent_id: The agent's ID.
        
        Returns:
            The response text or None if not found.
        """
        for resp in self.responses:
            if resp.agent_id == agent_id:
                return resp.response
        return None
    
    def response_count(self) -> int:
        """Get the number of responses collected.
        
        Returns:
            Number of agent responses.
        """
        return len(self.responses)
