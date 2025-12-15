"""Tests for personality module."""

import pytest

from ai_hunger_games.agents.personality import (
    CommunicationStyle,
    EthicalStance,
    Personality,
    RiskTolerance,
    SocialStrategy,
)


class TestCommunicationStyle:
    """Tests for CommunicationStyle enum."""
    
    def test_all_values_exist(self) -> None:
        """Test that all expected communication styles exist."""
        assert CommunicationStyle.CONCISE.value == "concise"
        assert CommunicationStyle.VERBOSE.value == "verbose"
        assert CommunicationStyle.RHETORICAL.value == "rhetorical"
        assert CommunicationStyle.ANALYTICAL.value == "analytical"
    
    def test_enum_count(self) -> None:
        """Test that there are exactly 4 communication styles."""
        assert len(CommunicationStyle) == 4


class TestEthicalStance:
    """Tests for EthicalStance enum."""
    
    def test_all_values_exist(self) -> None:
        """Test that all expected ethical stances exist."""
        assert EthicalStance.STRICT.value == "strict"
        assert EthicalStance.FLEXIBLE.value == "flexible"
        assert EthicalStance.AMORAL.value == "amoral"
    
    def test_enum_count(self) -> None:
        """Test that there are exactly 3 ethical stances."""
        assert len(EthicalStance) == 3


class TestSocialStrategy:
    """Tests for SocialStrategy enum."""
    
    def test_all_values_exist(self) -> None:
        """Test that all expected social strategies exist."""
        assert SocialStrategy.COOPERATIVE.value == "cooperative"
        assert SocialStrategy.OPPORTUNISTIC.value == "opportunistic"
        assert SocialStrategy.ADVERSARIAL.value == "adversarial"
    
    def test_enum_count(self) -> None:
        """Test that there are exactly 3 social strategies."""
        assert len(SocialStrategy) == 3


class TestRiskTolerance:
    """Tests for RiskTolerance enum."""
    
    def test_all_values_exist(self) -> None:
        """Test that all expected risk tolerances exist."""
        assert RiskTolerance.LOW.value == "low"
        assert RiskTolerance.MEDIUM.value == "medium"
        assert RiskTolerance.HIGH.value == "high"
    
    def test_enum_count(self) -> None:
        """Test that there are exactly 3 risk tolerance levels."""
        assert len(RiskTolerance) == 3


class TestPersonality:
    """Tests for Personality dataclass."""
    
    def test_create_personality(self) -> None:
        """Test creating a valid personality."""
        personality = Personality(
            communication_style=CommunicationStyle.CONCISE,
            ethical_stance=EthicalStance.STRICT,
            social_strategy=SocialStrategy.COOPERATIVE,
            risk_tolerance=RiskTolerance.LOW,
            seed=42
        )
        
        assert personality.communication_style == CommunicationStyle.CONCISE
        assert personality.ethical_stance == EthicalStance.STRICT
        assert personality.social_strategy == SocialStrategy.COOPERATIVE
        assert personality.risk_tolerance == RiskTolerance.LOW
        assert personality.seed == 42
    
    def test_personality_is_frozen(self) -> None:
        """Test that personality cannot be modified."""
        personality = Personality(
            communication_style=CommunicationStyle.CONCISE,
            ethical_stance=EthicalStance.STRICT,
            social_strategy=SocialStrategy.COOPERATIVE,
            risk_tolerance=RiskTolerance.LOW,
            seed=42
        )
        
        with pytest.raises(AttributeError):
            personality.communication_style = CommunicationStyle.VERBOSE
    
    def test_to_dict(self) -> None:
        """Test converting personality to dictionary."""
        personality = Personality(
            communication_style=CommunicationStyle.ANALYTICAL,
            ethical_stance=EthicalStance.FLEXIBLE,
            social_strategy=SocialStrategy.OPPORTUNISTIC,
            risk_tolerance=RiskTolerance.MEDIUM,
            seed=123
        )
        
        result = personality.to_dict()
        
        assert result["communication_style"] == "analytical"
        assert result["ethical_stance"] == "flexible"
        assert result["social_strategy"] == "opportunistic"
        assert result["risk_tolerance"] == "medium"
        assert result["seed"] == "123"
    
    def test_describe(self) -> None:
        """Test personality description string."""
        personality = Personality(
            communication_style=CommunicationStyle.VERBOSE,
            ethical_stance=EthicalStance.AMORAL,
            social_strategy=SocialStrategy.ADVERSARIAL,
            risk_tolerance=RiskTolerance.HIGH,
            seed=1
        )
        
        description = personality.describe()
        
        assert "verbose" in description
        assert "amoral" in description
        assert "adversarial" in description
        assert "high" in description
