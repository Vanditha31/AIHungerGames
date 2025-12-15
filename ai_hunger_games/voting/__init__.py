"""Voting module - vote aggregation and tie-breaking."""

from ai_hunger_games.voting.aggregation import aggregate_votes
from ai_hunger_games.voting.strategy import (
    InvalidVoteError,
    SelfVoteError,
    collect_votes,
)
from ai_hunger_games.voting.types import Vote, VoteResult, VotingRoundResult

__all__ = [
    "InvalidVoteError",
    "SelfVoteError",
    "Vote",
    "VoteResult",
    "VotingRoundResult",
    "aggregate_votes",
    "collect_votes",
]
