"""Ollama client for AI Hunger Games.

Provides connectivity to local Ollama instance for health checks and model listing.
No model inference calls are made in Phase 0 - only connectivity verification.
"""

from dataclasses import dataclass

import httpx

from ai_hunger_games.core.logging_setup import get_logger


logger = get_logger(__name__)


class OllamaConnectionError(Exception):
    """Raised when Ollama is not reachable or returns an error."""
    
    pass


@dataclass(frozen=True)
class OllamaModel:
    """Represents an available Ollama model."""
    
    name: str
    size: int


class OllamaClient:
    """Client for interacting with local Ollama instance.
    
    Provides health checks and model listing functionality.
    All Ollama interactions in the arena must go through this client.
    """
    
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        """Initialize Ollama client.
        
        Args:
            base_url: Base URL of Ollama API (e.g., http://localhost:11434).
            timeout: Request timeout in seconds.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(timeout=timeout)
    
    def health_check(self) -> bool:
        """Check if Ollama is running and reachable.
        
        Returns:
            True if Ollama responds successfully, False otherwise.
        """
        try:
            response = self._client.get(f"{self._base_url}/api/tags")
            is_healthy = response.status_code == 200
            
            if is_healthy:
                logger.info("Ollama health check passed")
            else:
                logger.warning(
                    f"Ollama health check failed: status {response.status_code}"
                )
            
            return is_healthy
        except httpx.RequestError as e:
            logger.error(f"Ollama connection failed: {e}")
            return False
    
    def list_models(self) -> list[OllamaModel]:
        """List available models in Ollama.
        
        Returns:
            List of available OllamaModel instances.
        
        Raises:
            OllamaConnectionError: If Ollama is not reachable.
        """
        try:
            response = self._client.get(f"{self._base_url}/api/tags")
            response.raise_for_status()
        except httpx.RequestError as e:
            raise OllamaConnectionError(
                f"Failed to connect to Ollama: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise OllamaConnectionError(
                f"Ollama returned error: {e.response.status_code}"
            ) from e
        
        data = response.json()
        models = []
        
        for model_data in data.get("models", []):
            model = OllamaModel(
                name=model_data.get("name", "unknown"),
                size=model_data.get("size", 0),
            )
            models.append(model)
        
        logger.info(f"Found {len(models)} models in Ollama")
        return models
    
    def check_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available in Ollama.
        
        Args:
            model_name: Name of the model to check.
        
        Returns:
            True if model is available, False otherwise.
        """
        try:
            models = self.list_models()
            available = any(m.name == model_name for m in models)
            
            if available:
                logger.info(f"Model '{model_name}' is available")
            else:
                logger.warning(f"Model '{model_name}' not found in Ollama")
            
            return available
        except OllamaConnectionError:
            return False
    
    def close(self) -> None:
        """Close the HTTP client connection."""
        self._client.close()
    
    def __enter__(self) -> "OllamaClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - closes client."""
        self.close()
