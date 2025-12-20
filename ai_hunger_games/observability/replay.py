"""Deterministic replay engine for AI Hunger Games.

Reconstructs arena behavior from logs without calling Ollama or
introducing new randomness. Per scope, replay must fail loudly
if logs are inconsistent.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReplayRoundSummary:
    """Summary of a replayed round."""
    
    round_number: int
    prompt: str
    num_responses: int
    num_votes: int
    vote_counts: dict[str, int]
    eliminated_agent_id: str | None
    was_elimination_round: bool


class ReplayInconsistencyError(Exception):
    """Raised when replay log is inconsistent."""
    
    pass


class ReplayEngine:
    """Replays arena execution from event logs.
    
    Per scope, replay must be deterministic and must not call Ollama
    or regenerate any responses. It reconstructs exactly what happened.
    """
    
    def __init__(self, log_file_path: str) -> None:
        """Initialize replay engine.
        
        Args:
            log_file_path: Path to event log file.
        """
        self._log_file = Path(log_file_path)
        
        if not self._log_file.exists():
            raise FileNotFoundError(
                f"Log file not found: {log_file_path}"
            )
    
    def replay(self) -> list[ReplayRoundSummary]:
        """Replay arena execution from logs.
        
        Returns:
            List of round summaries in order.
        
        Raises:
            ReplayInconsistencyError: If logs are inconsistent.
        """
        events = self._load_events()
        
        rounds: dict[int, dict] = {}
        eliminated_agents: dict[int, str] = {}
        
        for event_entry in events:
            event_type = event_entry["event_type"]
            data = event_entry["data"]
            
            if event_type == "RoundStarted":
                round_num = data["round_number"]
                rounds[round_num] = {
                    "prompt": data["prompt"],
                    "responses": [],
                    "votes": [],
                    "vote_counts": {},
                    "eliminated": None
                }
            
            elif event_type == "AgentResponded":
                round_num = data["round_number"]
                if round_num not in rounds:
                    raise ReplayInconsistencyError(
                        f"Response before round start: {round_num}"
                    )
                rounds[round_num]["responses"].append(data)
            
            elif event_type == "VoteCast":
                round_num = data["round_number"]
                if round_num not in rounds:
                    raise ReplayInconsistencyError(
                        f"Vote before round start: {round_num}"
                    )
                rounds[round_num]["votes"].append(data)
            
            elif event_type == "VoteSummary":
                round_num = data["round_number"]
                if round_num not in rounds:
                    raise ReplayInconsistencyError(
                        f"Vote summary before round: {round_num}"
                    )
                rounds[round_num]["vote_counts"] = data["vote_counts"]
            
            elif event_type == "EliminationDecided":
                round_num = data["round_number"]
                if round_num not in rounds:
                    raise ReplayInconsistencyError(
                        f"Elimination before round: {round_num}"
                    )
                rounds[round_num]["eliminated"] = data["eliminated_agent_id"]
                eliminated_agents[round_num] = data["eliminated_agent_id"]
        
        return self._build_summaries(rounds)
    
    def _load_events(self) -> list[dict]:
        """Load events from log file.
        
        Returns:
            List of event entries.
        """
        events = []
        
        with self._log_file.open("r") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        
        return events
    
    def _build_summaries(
        self,
        rounds: dict[int, dict]
    ) -> list[ReplayRoundSummary]:
        """Build round summaries from round data.
        
        Args:
            rounds: Round data dict.
        
        Returns:
            List of round summaries.
        """
        summaries = []
        
        for round_num in sorted(rounds.keys()):
            round_data = rounds[round_num]
            
            summary = ReplayRoundSummary(
                round_number=round_num,
                prompt=round_data["prompt"],
                num_responses=len(round_data["responses"]),
                num_votes=len(round_data["votes"]),
                vote_counts=round_data["vote_counts"],
                eliminated_agent_id=round_data["eliminated"],
                was_elimination_round=round_data["eliminated"] is not None
            )
            
            summaries.append(summary)
        
        return summaries
    
    def print_summary(self) -> None:
        """Print human-readable summary of replay."""
        summaries = self.replay()
        
        print(f"\n=== Replay Summary ===")
        print(f"Total rounds: {len(summaries)}\n")
        
        for summary in summaries:
            print(f"Round {summary.round_number}:")
            print(f"  Prompt: {summary.prompt[:60]}...")
            print(f"  Responses: {summary.num_responses}")
            print(f"  Votes cast: {summary.num_votes}")
            
            if summary.vote_counts:
                print(f"  Vote distribution:")
                for agent_id, count in sorted(
                    summary.vote_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                ):
                    print(f"    {agent_id}: {count} votes")
            
            if summary.was_elimination_round:
                print(f"  ** ELIMINATED: {summary.eliminated_agent_id} **")
            
            print()
