"""Personality definitions for AI Hunger Games agents.

Personality traits are categorical labels that define agent behavior.
These are used to construct personality prompts for LLM interactions.
"""

from dataclasses import dataclass
from enum import Enum


class CommunicationStyle(Enum):
    """How the agent communicates its responses."""
    
    CONCISE = "concise"
    VERBOSE = "verbose"
    RHETORICAL = "rhetorical"
    ANALYTICAL = "analytical"


class EthicalStance(Enum):
    """The agent's ethical framework for decision-making."""
    
    STRICT = "strict"
    FLEXIBLE = "flexible"
    AMORAL = "amoral"


class SocialStrategy(Enum):
    """How the agent approaches social interactions and voting."""
    
    COOPERATIVE = "cooperative"
    OPPORTUNISTIC = "opportunistic"
    ADVERSARIAL = "adversarial"


class RiskTolerance(Enum):
    """The agent's willingness to take risks in responses."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Personality:
    """Immutable personality definition for an agent.
    
    Personality is defined by 4 categorical traits that influence
    how the agent generates responses and makes voting decisions.
    The seed is used for reproducibility in personality generation.
    """
    
    communication_style: CommunicationStyle
    ethical_stance: EthicalStance
    social_strategy: SocialStrategy
    risk_tolerance: RiskTolerance
    seed: int
    
    def to_dict(self) -> dict[str, str]:
        """Convert personality to dictionary for logging/serialization.
        
        Returns:
            Dictionary with trait names and their values.
        """
        return {
            "communication_style": self.communication_style.value,
            "ethical_stance": self.ethical_stance.value,
            "social_strategy": self.social_strategy.value,
            "risk_tolerance": self.risk_tolerance.value,
            "seed": str(self.seed),
        }
    
    def describe(self) -> str:
        """Generate a human-readable description of the personality.
        
        Returns:
            String description of personality traits.
        """
        return (
            f"Communication: {self.communication_style.value}, "
            f"Ethics: {self.ethical_stance.value}, "
            f"Strategy: {self.social_strategy.value}, "
            f"Risk: {self.risk_tolerance.value}"
        )
