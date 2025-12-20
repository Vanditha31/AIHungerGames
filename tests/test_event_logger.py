"""Tests for event logger module."""

import json
import tempfile
from pathlib import Path

from ai_hunger_games.observability.logger import EventLogger


class TestEventLogger:
    """Tests for EventLogger class."""
    
    def test_create_logger(self) -> None:
        """Test creating an event logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = EventLogger(str(log_file))
            
            assert log_file.exists()
    
    def test_log_round_started(self) -> None:
        """Test logging round started event."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = EventLogger(str(log_file))
            
            logger.log_round_started(round_number=1, prompt="Test prompt")
            
            with log_file.open("r") as f:
                line = f.readline()
                entry = json.loads(line)
                
                assert entry["event_type"] == "RoundStarted"
                assert entry["data"]["round_number"] == 1
                assert entry["data"]["prompt"] == "Test prompt"
    
    def test_log_vote_cast(self) -> None:
        """Test logging vote cast event."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = EventLogger(str(log_file))
            
            logger.log_vote_cast(
                round_number=1,
                voter_id="agent_1",
                voted_for_id="agent_2"
            )
            
            with log_file.open("r") as f:
                line = f.readline()
                entry = json.loads(line)
                
                assert entry["event_type"] == "VoteCast"
                assert entry["data"]["voter_id"] == "agent_1"
                assert entry["data"]["voted_for_id"] == "agent_2"
    
    def test_append_only(self) -> None:
        """Test that logger appends to existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = EventLogger(str(log_file))
            
            logger.log_round_started(round_number=1, prompt="Prompt 1")
            logger.log_round_started(round_number=2, prompt="Prompt 2")
            
            with log_file.open("r") as f:
                lines = f.readlines()
                
                assert len(lines) == 2
