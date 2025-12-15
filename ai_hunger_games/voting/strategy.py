"""Voting strategy implementations for AI Hunger Games.

Implements single-choice voting where each agent votes for exactly
one other agent. Self-voting is explicitly forbidden per CODING_RULES.md.
"""

from ai_hunger_games.arena.round_state import RoundState
from ai_hunger_games.voting.types import Vote


class SelfVoteError(Exception):
    """Raised when an agent attempts to vote for itself."""
    
    pass


class InvalidVoteError(Exception):
    """Raised when a vote target is invalid."""
    
    pass


def collect_votes(
    round_state: RoundState,
    vote_choices: dict[str, str]
) -> list[Vote]:
    """Collect votes from all agents for a round.
    
    Validates that no agent votes for itself and that all
    vote targets exist in the round.
    
    Args:
        round_state: The completed round state with all responses.
        vote_choices: Mapping of voter_id to voted_for_id.
    
    Returns:
        List of validated Vote objects.
    
    Raises:
        SelfVoteError: If any agent votes for itself.
        InvalidVoteError: If vote target doesn't exist.
    """
    votes = []
    agent_ids = {resp.agent_id for resp in round_state.responses}
    
    for voter_id, voted_for_id in vote_choices.items():
        if voter_id == voted_for_id:
            raise SelfVoteError(
                f"Agent '{voter_id}' cannot vote for itself"
            )
        
        if voted_for_id not in agent_ids:
            raise InvalidVoteError(
                f"Vote target '{voted_for_id}' not found in round"
            )
        
        vote = Vote(
            voter_id=voter_id,
            voted_for_id=voted_for_id,
            round_number=round_state.round_number
        )
        votes.append(vote)
    
    return votes
