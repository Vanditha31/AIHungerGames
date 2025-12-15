"""Personality generation for AI Hunger Games.

Generates new agent personalities deterministically using seeded randomness.
Per PROJECT.md, personalities are generated from a fixed template without
inheritance or learning from previous agents.
"""

import random
from typing import Optional

from ai_hunger_games.agents.personality import (
    CommunicationStyle,
    EthicalStance,
    Personality,
    RiskTolerance,
    SocialStrategy,
)


class PersonalityGenerator:
    """Generates personalities using seeded randomness.
    
    Uses a fixed template approach where each trait is randomly selected
    from predefined categories. No inheritance or learning occurs.
    Per PROJECT.md Decision #2: high variation at initialization.
    """
    
    def __init__(self, base_seed: int) -> None:
        """Initialize the personality generator.
        
        Args:
            base_seed: Base random seed for reproducibility.
        """
        self._base_seed = base_seed
        self._generation_count = 0
    
    def generate(self, agent_id: Optional[str] = None) -> Personality:
        """Generate a new personality.
        
        Uses base seed + generation count to ensure each personality
        is unique but deterministic given the same base seed.
        
        Args:
            agent_id: Optional agent ID for seed variation.
        
        Returns:
            A randomly generated personality.
        """
        seed = self._compute_seed(agent_id)
        rng = random.Random(seed)
        
        personality = Personality(
            communication_style=rng.choice(list(CommunicationStyle)),
            ethical_stance=rng.choice(list(EthicalStance)),
            social_strategy=rng.choice(list(SocialStrategy)),
            risk_tolerance=rng.choice(list(RiskTolerance)),
            seed=seed
        )
        
        self._generation_count += 1
        
        return personality
    
    def _compute_seed(self, agent_id: Optional[str]) -> int:
        """Compute seed for personality generation.
        
        Args:
            agent_id: Optional agent ID for additional variation.
        
        Returns:
            Computed seed value.
        """
        seed = self._base_seed + self._generation_count
        
        if agent_id:
            seed ^= hash(agent_id)
        
        return seed
