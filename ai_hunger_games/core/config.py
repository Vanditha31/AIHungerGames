"""Configuration management for AI Hunger Games.

Loads settings from YAML config file with optional CLI overrides.
All configuration is validated and typed via the Settings dataclass.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass(frozen=True)
class Settings:
    """Immutable configuration settings for the arena.
    
    All required configuration keys are defined here with their types.
    Configuration is frozen to prevent accidental mutation during a run.
    """
    
    model_name: str
    temperature: float
    ollama_base_url: str
    num_agents: int
    rounds_per_elimination: int
    memory_window: int
    random_seed: int
    log_level: str
    log_file: str


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required keys."""
    
    pass


def load_config(
    config_path: Path,
    overrides: Optional[dict[str, str | int | float]] = None
) -> Settings:
    """Load configuration from YAML file with optional overrides.
    
    Args:
        config_path: Path to the YAML configuration file.
        overrides: Optional dictionary of CLI overrides to apply.
    
    Returns:
        Validated Settings instance.
    
    Raises:
        ConfigError: If config file is missing or has invalid/missing keys.
    """
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")
    
    raw_config = _load_yaml(config_path)
    
    if overrides:
        raw_config = _apply_overrides(raw_config, overrides)
    
    return _validate_and_build(raw_config)


def _load_yaml(config_path: Path) -> dict:
    """Load and parse YAML configuration file."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in config file: {e}") from e
    
    if config is None:
        raise ConfigError("Configuration file is empty")
    
    return config


def _apply_overrides(
    config: dict, 
    overrides: dict[str, str | int | float]
) -> dict:
    """Apply CLI overrides to configuration."""
    merged = config.copy()
    for key, value in overrides.items():
        if key in merged:
            merged[key] = value
    return merged


def _validate_and_build(config: dict) -> Settings:
    """Validate configuration and build Settings instance."""
    required_keys = {
        "model_name": str,
        "temperature": float,
        "ollama_base_url": str,
        "num_agents": int,
        "rounds_per_elimination": int,
        "memory_window": int,
        "random_seed": int,
        "log_level": str,
        "log_file": str,
    }
    
    for key, expected_type in required_keys.items():
        if key not in config:
            raise ConfigError(f"Missing required config key: {key}")
        
        value = config[key]
        if not isinstance(value, expected_type):
            if expected_type == float and isinstance(value, int):
                config[key] = float(value)
            else:
                raise ConfigError(
                    f"Invalid type for {key}: expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
    
    return Settings(
        model_name=config["model_name"],
        temperature=config["temperature"],
        ollama_base_url=config["ollama_base_url"],
        num_agents=config["num_agents"],
        rounds_per_elimination=config["rounds_per_elimination"],
        memory_window=config["memory_window"],
        random_seed=config["random_seed"],
        log_level=config["log_level"],
        log_file=config["log_file"],
    )
