"""Post-mortem data capture for eliminated agents.

Captures observational metadata about eliminated agents.
Per PROJECT.md Decision #9, this is metadata only and NOT fed back
into personality generation in the MVP.
"""

from dataclasses import dataclass

from ai_hunger_games.agents.personality import Personality


@dataclass(frozen=True)
class PostMortemRecord:
    """Observational record of an eliminated agent.
    
    Captures metadata about the agent's performance for potential
    future analysis. This data is NOT used for personality generation
    in the MVP per PROJECT.md Decision #9.
    """
    
    agent_id: str
    personality: Personality
    rounds_survived: int
    total_votes_received: int
    elimination_round: int
    was_tie: bool
    
    def to_dict(self) -> dict[str, object]:
        """Convert post-mortem record to dictionary.
        
        Returns:
            Dictionary representation for logging/storage.
        """
        return {
            "agent_id": self.agent_id,
            "personality": self.personality.to_dict(),
            "rounds_survived": self.rounds_survived,
            "total_votes_received": self.total_votes_received,
            "elimination_round": self.elimination_round,
            "was_tie": self.was_tie,
        }
