"""Vote aggregation for AI Hunger Games.

Aggregates individual votes into round results with vote counts.
Pure functions with deterministic behavior.
"""

from ai_hunger_games.voting.types import Vote, VoteResult, VotingRoundResult


def aggregate_votes(
    votes: list[Vote],
    round_number: int,
    all_agent_ids: list[str]
) -> VotingRoundResult:
    """Aggregate individual votes into round results.
    
    Counts votes received by each agent. Agents with zero votes
    are included with votes_received=0.
    
    Args:
        votes: List of individual votes cast.
        round_number: The round number.
        all_agent_ids: All agent IDs to include in results.
    
    Returns:
        Complete voting round result with aggregated counts.
    """
    vote_counts: dict[str, int] = {
        agent_id: 0 for agent_id in all_agent_ids
    }
    
    for vote in votes:
        if vote.voted_for_id in vote_counts:
            vote_counts[vote.voted_for_id] += 1
    
    results = tuple(
        VoteResult(agent_id=agent_id, votes_received=count)
        for agent_id, count in sorted(vote_counts.items())
    )
    
    return VotingRoundResult(
        round_number=round_number,
        votes=tuple(votes),
        results=results
    )
