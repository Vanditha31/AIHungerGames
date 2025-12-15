"""Data structures for voting in AI Hunger Games.

Defines immutable vote records and aggregated results.
Per ARCHITECTURE.md, voting is single-choice with self-voting forbidden.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Vote:
    """A single vote cast by an agent.
    
    Represents one agent voting for another agent's response.
    Self-voting is forbidden and must be validated elsewhere.
    """
    
    voter_id: str
    voted_for_id: str
    round_number: int


@dataclass(frozen=True)
class VoteResult:
    """Aggregated vote result for a single agent.
    
    Contains the total number of votes received by one agent.
    """
    
    agent_id: str
    votes_received: int


@dataclass(frozen=True)
class VotingRoundResult:
    """Complete voting results for a round.
    
    Contains all individual votes and aggregated results.
    """
    
    round_number: int
    votes: tuple[Vote, ...]
    results: tuple[VoteResult, ...]
    
    def get_votes_for(self, agent_id: str) -> int:
        """Get the number of votes received by an agent.
        
        Args:
            agent_id: The agent to query.
        
        Returns:
            Number of votes received.
        """
        for result in self.results:
            if result.agent_id == agent_id:
                return result.votes_received
        return 0
