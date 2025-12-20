"""Tests for replay engine module."""

import json
import tempfile
from pathlib import Path

import pytest

from ai_hunger_games.observability.replay import (
    ReplayEngine,
    ReplayInconsistencyError,
)


class TestReplayEngine:
    """Tests for ReplayEngine class."""
    
    def test_replay_simple_round(self) -> None:
        """Test replaying a simple round."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            # Write mock events
            events = [
                {"event_type": "RoundStarted", "data": {"round_number": 1, "prompt": "Test", "timestamp": "2024-01-01T00:00:00"}},
                {"event_type": "AgentResponded", "data": {"round_number": 1, "agent_id": "agent_1", "response": "Response", "timestamp": "2024-01-01T00:00:01"}},
                {"event_type": "VoteSummary", "data": {"round_number": 1, "vote_counts": {"agent_1": 0}, "timestamp": "2024-01-01T00:00:02"}},
            ]
            
            with log_file.open("w") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
            
            engine = ReplayEngine(str(log_file))
            summaries = engine.replay()
            
            assert len(summaries) == 1
            assert summaries[0].round_number == 1
            assert summaries[0].prompt == "Test"
            assert summaries[0].num_responses == 1
    
    def test_replay_with_elimination(self) -> None:
        """Test replaying with elimination."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            events = [
                {"event_type": "RoundStarted", "data": {"round_number": 1, "prompt": "Test", "timestamp": "2024-01-01T00:00:00"}},
                {"event_type": "VoteSummary", "data": {"round_number": 1, "vote_counts": {"agent_1": 5}, "timestamp": "2024-01-01T00:00:01"}},
                {"event_type": "EliminationDecided", "data": {"round_number": 1, "eliminated_agent_id": "agent_1", "cumulative_votes": 5, "was_tie": False, "timestamp": "2024-01-01T00:00:02"}},
            ]
            
            with log_file.open("w") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
            
            engine = ReplayEngine(str(log_file))
            summaries = engine.replay()
            
            assert len(summaries) == 1
            assert summaries[0].was_elimination_round is True
            assert summaries[0].eliminated_agent_id == "agent_1"
    
    def test_replay_nonexistent_file_raises(self) -> None:
        """Test that replaying nonexistent file raises."""
        with pytest.raises(FileNotFoundError):
            ReplayEngine("/nonexistent/file.log")
    
    def test_replay_inconsistent_logs_raises(self) -> None:
        """Test that inconsistent logs raise error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            # Vote before round start - inconsistent
            events = [
                {"event_type": "VoteCast", "data": {"round_number": 1, "voter_id": "agent_1", "voted_for_id": "agent_2", "timestamp": "2024-01-01T00:00:00"}},
            ]
            
            with log_file.open("w") as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
            
            engine = ReplayEngine(str(log_file))
            
            with pytest.raises(ReplayInconsistencyError):
                engine.replay()
