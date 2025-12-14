"""Tests for configuration loading and validation."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from ai_hunger_games.core.config import ConfigError, Settings, load_config


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Test loading a valid configuration file."""
        config_content = """
model_name: "llama3.1:8b"
temperature: 0.2
ollama_base_url: "http://localhost:11434"
num_agents: 8
rounds_per_elimination: 2
memory_window: 5
random_seed: 42
log_level: "INFO"
log_file: "logs/arena.log"
"""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text(config_content)
        
        settings = load_config(config_file)
        
        assert isinstance(settings, Settings)
        assert settings.model_name == "llama3.1:8b"
        assert settings.temperature == 0.2
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.num_agents == 8
        assert settings.rounds_per_elimination == 2
        assert settings.memory_window == 5
        assert settings.random_seed == 42
        assert settings.log_level == "INFO"
        assert settings.log_file == "logs/arena.log"
    
    def test_load_config_with_int_temperature(self, tmp_path: Path) -> None:
        """Test that integer temperature is converted to float."""
        config_content = """
model_name: "llama3.1:8b"
temperature: 0
ollama_base_url: "http://localhost:11434"
num_agents: 8
rounds_per_elimination: 2
memory_window: 5
random_seed: 42
log_level: "INFO"
log_file: "logs/arena.log"
"""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text(config_content)
        
        settings = load_config(config_file)
        
        assert settings.temperature == 0.0
        assert isinstance(settings.temperature, float)
    
    def test_load_config_file_not_found(self) -> None:
        """Test that missing config file raises ConfigError."""
        with pytest.raises(ConfigError, match="Configuration file not found"):
            load_config(Path("/nonexistent/path/config.yaml"))
    
    def test_load_config_missing_required_key(self, tmp_path: Path) -> None:
        """Test that missing required key raises ConfigError."""
        config_content = """
model_name: "llama3.1:8b"
temperature: 0.2
"""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text(config_content)
        
        with pytest.raises(ConfigError, match="Missing required config key"):
            load_config(config_file)
    
    def test_load_config_invalid_type(self, tmp_path: Path) -> None:
        """Test that invalid type raises ConfigError."""
        config_content = """
model_name: "llama3.1:8b"
temperature: "not_a_number"
ollama_base_url: "http://localhost:11434"
num_agents: 8
rounds_per_elimination: 2
memory_window: 5
random_seed: 42
log_level: "INFO"
log_file: "logs/arena.log"
"""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text(config_content)
        
        with pytest.raises(ConfigError, match="Invalid type for temperature"):
            load_config(config_file)
    
    def test_load_config_empty_file(self, tmp_path: Path) -> None:
        """Test that empty config file raises ConfigError."""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text("")
        
        with pytest.raises(ConfigError, match="Configuration file is empty"):
            load_config(config_file)
    
    def test_load_config_with_overrides(self, tmp_path: Path) -> None:
        """Test that CLI overrides are applied correctly."""
        config_content = """
model_name: "llama3.1:8b"
temperature: 0.2
ollama_base_url: "http://localhost:11434"
num_agents: 8
rounds_per_elimination: 2
memory_window: 5
random_seed: 42
log_level: "INFO"
log_file: "logs/arena.log"
"""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text(config_content)
        
        overrides = {
            "num_agents": 4,
            "temperature": 0.5,
        }
        
        settings = load_config(config_file, overrides=overrides)
        
        assert settings.num_agents == 4
        assert settings.temperature == 0.5
        assert settings.model_name == "llama3.1:8b"


class TestSettingsImmutability:
    """Tests for Settings dataclass immutability."""
    
    def test_settings_is_frozen(self, tmp_path: Path) -> None:
        """Test that Settings cannot be modified after creation."""
        config_content = """
model_name: "llama3.1:8b"
temperature: 0.2
ollama_base_url: "http://localhost:11434"
num_agents: 8
rounds_per_elimination: 2
memory_window: 5
random_seed: 42
log_level: "INFO"
log_file: "logs/arena.log"
"""
        config_file = tmp_path / "settings.yaml"
        config_file.write_text(config_content)
        
        settings = load_config(config_file)
        
        with pytest.raises(AttributeError):
            settings.num_agents = 10
