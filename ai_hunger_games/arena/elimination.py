"""Elimination logic for AI Hunger Games.

Determines which agent should be eliminated based on cumulative votes.
Implements deterministic tie-breaking per ARCHITECTURE.md.
"""

from dataclasses import dataclass

from ai_hunger_games.voting.types import VotingRoundResult


@dataclass(frozen=True)
class EliminationCandidate:
    """A candidate for elimination with their score.
    
    Score is cumulative votes received against the agent.
    """
    
    agent_id: str
    cumulative_votes: int
    historical_average: float


@dataclass(frozen=True)
class EliminationResult:
    """Result of an elimination decision.
    
    Contains the eliminated agent ID and elimination reason.
    """
    
    eliminated_agent_id: str
    cumulative_votes: int
    was_tie: bool


def determine_elimination(
    candidates: list[EliminationCandidate],
    seed: int
) -> EliminationResult:
    """Determine which agent should be eliminated.
    
    Elimination is based on highest cumulative votes received.
    Ties are broken deterministically by:
    1. Lowest historical vote average
    2. If still tied, deterministic sort by agent_id XOR seed
    
    Args:
        candidates: List of all agents with cumulative scores.
        seed: Random seed for deterministic tie-breaking.
    
    Returns:
        Elimination result with eliminated agent ID.
    
    Raises:
        ValueError: If candidates list is empty.
    """
    if not candidates:
        raise ValueError("Cannot determine elimination with no candidates")
    
    max_votes = max(c.cumulative_votes for c in candidates)
    tied = [c for c in candidates if c.cumulative_votes == max_votes]
    
    was_tie = len(tied) > 1
    
    if len(tied) == 1:
        eliminated = tied[0]
    else:
        eliminated = _break_tie(tied, seed)
    
    return EliminationResult(
        eliminated_agent_id=eliminated.agent_id,
        cumulative_votes=eliminated.cumulative_votes,
        was_tie=was_tie
    )


def _break_tie(
    tied_candidates: list[EliminationCandidate],
    seed: int
) -> EliminationCandidate:
    """Break tie deterministically using historical average then seed.
    
    Args:
        tied_candidates: Candidates with same cumulative votes.
        seed: Random seed for final tie-breaking.
    
    Returns:
        The selected candidate for elimination.
    """
    min_avg = min(c.historical_average for c in tied_candidates)
    avg_tied = [c for c in tied_candidates if c.historical_average == min_avg]
    
    if len(avg_tied) == 1:
        return avg_tied[0]
    
    return sorted(
        avg_tied,
        key=lambda c: hash(c.agent_id) ^ seed
    )[0]
