"""Tests for Ollama client connectivity."""

import pytest
from unittest.mock import MagicMock, patch

import httpx

from ai_hunger_games.core.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaModel,
)


class TestOllamaClientHealthCheck:
    """Tests for OllamaClient.health_check method."""
    
    def test_health_check_success(self) -> None:
        """Test health check returns True when Ollama responds."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            client = OllamaClient("http://localhost:11434")
            result = client.health_check()
            
            assert result is True
            mock_get.assert_called_once_with("http://localhost:11434/api/tags")
    
    def test_health_check_failure_status(self) -> None:
        """Test health check returns False on non-200 status."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            client = OllamaClient("http://localhost:11434")
            result = client.health_check()
            
            assert result is False
    
    def test_health_check_connection_error(self) -> None:
        """Test health check returns False on connection error."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")
            
            client = OllamaClient("http://localhost:11434")
            result = client.health_check()
            
            assert result is False


class TestOllamaClientListModels:
    """Tests for OllamaClient.list_models method."""
    
    def test_list_models_success(self) -> None:
        """Test listing models returns parsed model data."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "llama3.1:8b", "size": 4000000000},
                    {"name": "mistral:7b", "size": 3500000000},
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            client = OllamaClient("http://localhost:11434")
            models = client.list_models()
            
            assert len(models) == 2
            assert models[0].name == "llama3.1:8b"
            assert models[0].size == 4000000000
            assert models[1].name == "mistral:7b"
    
    def test_list_models_empty(self) -> None:
        """Test listing models returns empty list when no models."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"models": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            client = OllamaClient("http://localhost:11434")
            models = client.list_models()
            
            assert len(models) == 0
    
    def test_list_models_connection_error(self) -> None:
        """Test listing models raises error on connection failure."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")
            
            client = OllamaClient("http://localhost:11434")
            
            with pytest.raises(OllamaConnectionError, match="Failed to connect"):
                client.list_models()


class TestOllamaClientCheckModelAvailable:
    """Tests for OllamaClient.check_model_available method."""
    
    def test_check_model_available_found(self) -> None:
        """Test model availability returns True when model exists."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "llama3.1:8b", "size": 4000000000},
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            client = OllamaClient("http://localhost:11434")
            result = client.check_model_available("llama3.1:8b")
            
            assert result is True
    
    def test_check_model_available_not_found(self) -> None:
        """Test model availability returns False when model missing."""
        with patch.object(httpx.Client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "mistral:7b", "size": 3500000000},
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            client = OllamaClient("http://localhost:11434")
            result = client.check_model_available("llama3.1:8b")
            
            assert result is False


class TestOllamaClientContextManager:
    """Tests for OllamaClient context manager."""
    
    def test_context_manager_closes_client(self) -> None:
        """Test that context manager closes the HTTP client."""
        with patch.object(httpx.Client, "close") as mock_close:
            with OllamaClient("http://localhost:11434") as client:
                pass
            
            mock_close.assert_called_once()
