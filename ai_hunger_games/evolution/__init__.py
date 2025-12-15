"""Evolution module - personality generation and agent replacement."""

from ai_hunger_games.evolution.personality_generator import PersonalityGenerator
from ai_hunger_games.evolution.post_mortem import PostMortemRecord
from ai_hunger_games.evolution.replacement import AgentReplacementCoordinator

__all__ = [
    "AgentReplacementCoordinator",
    "PersonalityGenerator",
    "PostMortemRecord",
]
