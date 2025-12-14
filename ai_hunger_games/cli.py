"""Command-line interface for AI Hunger Games.

Provides CLI commands for arena operations and diagnostics.
No business logic here - just argument parsing and delegation to core modules.
"""

import argparse
import sys
from pathlib import Path

from ai_hunger_games.core.config import ConfigError, load_config
from ai_hunger_games.core.logging_setup import setup_logging, get_logger
from ai_hunger_games.core.ollama_client import OllamaClient


DEFAULT_CONFIG_PATH = Path("config/settings.yaml")


def main() -> int:
    """Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = _create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    if args.command == "check-ollama":
        return _check_ollama(args)
    
    return 0


def _create_parser() -> argparse.ArgumentParser:
    """Create argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="hunger-games",
        description="AI Hunger Games - Multi-agent LLM arena"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to config file (default: {DEFAULT_CONFIG_PATH})"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    check_parser = subparsers.add_parser(
        "check-ollama",
        help="Check Ollama connectivity and available models"
    )
    check_parser.add_argument(
        "--model",
        type=str,
        help="Specific model to check for availability"
    )
    
    return parser


def _check_ollama(args: argparse.Namespace) -> int:
    """Run Ollama connectivity check.
    
    Args:
        args: Parsed command-line arguments.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        settings = load_config(args.config)
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    
    setup_logging(settings.log_level)
    logger = get_logger("cli")
    
    logger.info(f"Checking Ollama at {settings.ollama_base_url}")
    
    with OllamaClient(settings.ollama_base_url) as client:
        if not client.health_check():
            print("❌ Ollama is not reachable", file=sys.stderr)
            print(
                f"   Make sure Ollama is running at {settings.ollama_base_url}",
                file=sys.stderr
            )
            return 1
        
        print("✅ Ollama is running")
        
        models = client.list_models()
        if models:
            print(f"\nAvailable models ({len(models)}):")
            for model in models:
                size_mb = model.size / (1024 * 1024)
                print(f"  - {model.name} ({size_mb:.1f} MB)")
        else:
            print("\nNo models found. Pull a model with: ollama pull llama3.1:8b")
        
        model_to_check = args.model or settings.model_name
        if client.check_model_available(model_to_check):
            print(f"\n✅ Required model '{model_to_check}' is available")
        else:
            print(
                f"\n⚠️  Required model '{model_to_check}' not found",
                file=sys.stderr
            )
            print(f"   Pull it with: ollama pull {model_to_check}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
