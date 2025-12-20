"""Structured event logger for AI Hunger Games.

Appends events to immutable JSON log files. Per scope, logs are
append-only and must not be modified once written.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_hunger_games.observability.events import (
    AgentReplacedEvent,
    AgentRespondedEvent,
    ArenaInitializedEvent,
    EliminationDecidedEvent,
    RoundStartedEvent,
    VoteCastEvent,
    VoteSummaryEvent,
)


class EventLogger:
    """Logs structured events to append-only JSON file.
    
    Per scope, logs are immutable once written and must support
    deterministic replay.
    """
    
    def __init__(self, log_file_path: str) -> None:
        """Initialize the event logger.
        
        Args:
            log_file_path: Path to JSON log file.
        """
        self._log_file = Path(log_file_path)
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if doesn't exist
        if not self._log_file.exists():
            self._log_file.write_text("")
    
    def log_arena_initialized(
        self,
        settings: dict[str, Any],
        agent_ids: list[str]
    ) -> None:
        """Log arena initialization."""
        event = ArenaInitializedEvent(
            num_agents=len(agent_ids),
            agent_ids=agent_ids,
            settings=settings,
            timestamp=self._timestamp()
        )
        self._append_event("ArenaInitialized", event)
    
    def log_round_started(
        self,
        round_number: int,
        prompt: str
    ) -> None:
        """Log round start."""
        event = RoundStartedEvent(
            round_number=round_number,
            prompt=prompt,
            timestamp=self._timestamp()
        )
        self._append_event("RoundStarted", event)
    
    def log_agent_responded(
        self,
        round_number: int,
        agent_id: str,
        response: str
    ) -> None:
        """Log agent response."""
        event = AgentRespondedEvent(
            round_number=round_number,
            agent_id=agent_id,
            response=response,
            timestamp=self._timestamp()
        )
        self._append_event("AgentResponded", event)
    
    def log_vote_cast(
        self,
        round_number: int,
        voter_id: str,
        voted_for_id: str
    ) -> None:
        """Log individual vote."""
        event = VoteCastEvent(
            round_number=round_number,
            voter_id=voter_id,
            voted_for_id=voted_for_id,
            timestamp=self._timestamp()
        )
        self._append_event("VoteCast", event)
    
    def log_vote_summary(
        self,
        round_number: int,
        vote_counts: dict[str, int]
    ) -> None:
        """Log aggregated vote summary."""
        event = VoteSummaryEvent(
            round_number=round_number,
            vote_counts=vote_counts,
            timestamp=self._timestamp()
        )
        self._append_event("VoteSummary", event)
    
    def log_elimination_decided(
        self,
        round_number: int,
        eliminated_agent_id: str,
        cumulative_votes: int,
        was_tie: bool
    ) -> None:
        """Log elimination decision."""
        event = EliminationDecidedEvent(
            round_number=round_number,
            eliminated_agent_id=eliminated_agent_id,
            cumulative_votes=cumulative_votes,
            was_tie=was_tie,
            timestamp=self._timestamp()
        )
        self._append_event("EliminationDecided", event)
    
    def log_agent_replaced(
        self,
        round_number: int,
        agent_id: str,
        old_personality: dict[str, Any],
        new_personality: dict[str, Any]
    ) -> None:
        """Log agent replacement."""
        event = AgentReplacedEvent(
            round_number=round_number,
            agent_id=agent_id,
            old_personality=old_personality,
            new_personality=new_personality,
            timestamp=self._timestamp()
        )
        self._append_event("AgentReplaced", event)
    
    def _append_event(
        self,
        event_type: str,
        event: Any
    ) -> None:
        """Append event to log file.
        
        Args:
            event_type: Type of event for deserialization.
            event: Event data.
        """
        log_entry = {
            "event_type": event_type,
            "data": self._to_dict(event)
        }
        
        with self._log_file.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _to_dict(self, event: Any) -> dict[str, Any]:
        """Convert event to dictionary."""
        if hasattr(event, "__dict__"):
            return {k: v for k, v in event.__dict__.items()}
        return event
    
    def _timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat()
