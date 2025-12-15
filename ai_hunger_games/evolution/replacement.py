"""Agent replacement coordination for AI Hunger Games.

Handles removing eliminated agents and creating replacements with
new personalities. Per ARCHITECTURE.md, this is evolution by
elimination without parameter tuning.
"""

from ai_hunger_games.agents.agent import Agent
from ai_hunger_games.agents.registry import AgentRegistry
from ai_hunger_games.core.logging_setup import get_logger
from ai_hunger_games.evolution.personality_generator import PersonalityGenerator
from ai_hunger_games.evolution.post_mortem import PostMortemRecord


logger = get_logger(__name__)


class AgentReplacementCoordinator:
    """Coordinates agent elimination and replacement.
    
    Handles the lifecycle of removing eliminated agents and creating
    new agents with fresh personalities. Per ARCHITECTURE.md, evolution
    happens through elimination, not parameter tuning.
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        generator: PersonalityGenerator,
        memory_window: int = 5
    ) -> None:
        """Initialize the replacement coordinator.
        
        Args:
            registry: The agent registry to modify.
            generator: Personality generator for new agents.
            memory_window: Memory window size for new agents.
        """
        self._registry = registry
        self._generator = generator
        self._memory_window = memory_window
        self._post_mortem_records: list[PostMortemRecord] = []
    
    def replace_agent(
        self,
        eliminated_agent_id: str,
        rounds_survived: int,
        total_votes_received: int,
        elimination_round: int,
        was_tie: bool
    ) -> Agent:
        """Replace an eliminated agent with a new agent.
        
        Creates post-mortem record, removes old agent, creates new
        agent with fresh personality.
        
        Args:
            eliminated_agent_id: ID of eliminated agent.
            rounds_survived: Number of rounds the agent survived.
            total_votes_received: Total votes against the agent.
            elimination_round: Round number of elimination.
            was_tie: Whether elimination involved a tie.
        
        Returns:
            The newly created replacement agent.
        """
        old_agent = self._registry.get(eliminated_agent_id)
        
        self._create_post_mortem(
            old_agent,
            rounds_survived,
            total_votes_received,
            elimination_round,
            was_tie
        )
        
        self._registry.remove(eliminated_agent_id)
        
        new_agent = self._create_replacement_agent(eliminated_agent_id)
        self._registry.register(new_agent)
        
        logger.info(
            f"Replaced agent '{eliminated_agent_id}': "
            f"old personality={old_agent.personality.describe()}, "
            f"new personality={new_agent.personality.describe()}"
        )
        
        return new_agent
    
    def _create_post_mortem(
        self,
        agent: Agent,
        rounds_survived: int,
        total_votes_received: int,
        elimination_round: int,
        was_tie: bool
    ) -> None:
        """Create post-mortem record for eliminated agent."""
        record = PostMortemRecord(
            agent_id=agent.agent_id,
            personality=agent.personality,
            rounds_survived=rounds_survived,
            total_votes_received=total_votes_received,
            elimination_round=elimination_round,
            was_tie=was_tie
        )
        
        self._post_mortem_records.append(record)
        
        logger.debug(
            f"Post-mortem recorded for '{agent.agent_id}': "
            f"{rounds_survived} rounds, {total_votes_received} votes"
        )
    
    def _create_replacement_agent(self, agent_id: str) -> Agent:
        """Create a new agent with fresh personality.
        
        Args:
            agent_id: ID for the new agent (reuses old ID).
        
        Returns:
            New agent with generated personality.
        """
        personality = self._generator.generate(agent_id)
        
        return Agent(
            agent_id=agent_id,
            personality=personality,
            memory_window=self._memory_window
        )
    
    def get_post_mortem_records(self) -> list[PostMortemRecord]:
        """Get all post-mortem records.
        
        Returns:
            List of all post-mortem records.
        """
        return list(self._post_mortem_records)
