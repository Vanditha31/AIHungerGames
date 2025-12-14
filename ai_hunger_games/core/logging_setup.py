"""Logging setup for AI Hunger Games.

Provides structured logging with console and file handlers.
All agent behavior is logged for explainability as per PROJECT.md constraints.
"""

import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure logging for the arena.
    
    Sets up structured logging with timestamp, level, module, and message.
    Console output goes to stderr; file output captures full run history.
    
    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to log file. Creates parent dirs if needed.
    """
    log_level = _parse_log_level(level)
    
    root_logger = logging.getLogger("ai_hunger_games")
    root_logger.setLevel(log_level)
    
    root_logger.handlers.clear()
    
    formatter = _create_formatter()
    
    console_handler = _create_console_handler(log_level, formatter)
    root_logger.addHandler(console_handler)
    
    if log_file:
        file_handler = _create_file_handler(log_file, log_level, formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the specified module.
    
    Args:
        name: Module name, typically __name__ from the calling module.
    
    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"ai_hunger_games.{name}")


def _parse_log_level(level: str) -> int:
    """Parse log level string to logging constant."""
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    normalized = level.upper()
    if normalized not in level_map:
        raise ValueError(
            f"Invalid log level: {level}. "
            f"Must be one of: {', '.join(level_map.keys())}"
        )
    
    return level_map[normalized]


def _create_formatter() -> logging.Formatter:
    """Create structured log formatter."""
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def _create_console_handler(
    level: int, 
    formatter: logging.Formatter
) -> logging.StreamHandler:
    """Create console handler for stderr output."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def _create_file_handler(
    log_file: str,
    level: int,
    formatter: logging.Formatter
) -> logging.FileHandler:
    """Create file handler with parent directory creation."""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler
