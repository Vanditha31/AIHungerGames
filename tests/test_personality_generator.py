"""Tests for personality generator module."""

import pytest

from ai_hunger_games.agents.personality import (
    CommunicationStyle,
    EthicalStance,
    Personality,
    RiskTolerance,
    SocialStrategy,
)
from ai_hunger_games.evolution.personality_generator import PersonalityGenerator


class TestPersonalityGenerator:
    """Tests for PersonalityGenerator class."""
    
    def test_generate_personality(self) -> None:
        """Test generating a personality."""
        generator = PersonalityGenerator(base_seed=42)
        
        personality = generator.generate()
        
        assert isinstance(personality, Personality)
        assert isinstance(personality.communication_style, CommunicationStyle)
        assert isinstance(personality.ethical_stance, EthicalStance)
        assert isinstance(personality.social_strategy, SocialStrategy)
        assert isinstance(personality.risk_tolerance, RiskTolerance)
        assert personality.seed > 0
    
    def test_deterministic_generation(self) -> None:
        """Test that same seed produces same personality."""
        gen1 = PersonalityGenerator(base_seed=42)
        gen2 = PersonalityGenerator(base_seed=42)
        
        p1 = gen1.generate()
        p2 = gen2.generate()
        
        assert p1.communication_style == p2.communication_style
        assert p1.ethical_stance == p2.ethical_stance
        assert p1.social_strategy == p2.social_strategy
        assert p1.risk_tolerance == p2.risk_tolerance
        assert p1.seed == p2.seed
    
    def test_different_seeds_produce_different_personalities(self) -> None:
        """Test that different seeds produce different personalities."""
        gen1 = PersonalityGenerator(base_seed=42)
        gen2 = PersonalityGenerator(base_seed=99)
        
        p1 = gen1.generate()
        p2 = gen2.generate()
        
        # Very unlikely to be identical with 4 independent traits
        assert p1.seed != p2.seed
    
    def test_multiple_generations_are_unique(self) -> None:
        """Test that multiple generations from same generator differ."""
        generator = PersonalityGenerator(base_seed=42)
        
        p1 = generator.generate()
        p2 = generator.generate()
        p3 = generator.generate()
        
        # Each should have different seed due to generation counter
        assert p1.seed != p2.seed
        assert p2.seed != p3.seed
        assert p1.seed != p3.seed
    
    def test_agent_id_affects_seed(self) -> None:
        """Test that agent_id parameter affects personality seed."""
        generator = PersonalityGenerator(base_seed=42)
        
        p1 = generator.generate(agent_id="agent_1")
        
        # Reset generator
        generator = PersonalityGenerator(base_seed=42)
        p2 = generator.generate(agent_id="agent_2")
        
        # Different agent IDs should produce different seeds
        assert p1.seed != p2.seed
    
    def test_generate_without_agent_id(self) -> None:
        """Test generating without specifying agent_id."""
        generator = PersonalityGenerator(base_seed=42)
        
        personality = generator.generate()
        
        assert isinstance(personality, Personality)
        assert personality.seed > 0
    
    def test_high_variation(self) -> None:
        """Test that generator produces varied personalities."""
        generator = PersonalityGenerator(base_seed=42)
        
        personalities = [generator.generate() for _ in range(20)]
        
        # Check we get different communication styles
        styles = {p.communication_style for p in personalities}
        assert len(styles) > 1  # Should have variation
        
        # Check we get different ethical stances
        stances = {p.ethical_stance for p in personalities}
        assert len(stances) > 1
