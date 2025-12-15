"""Arena controller for orchestrating rounds.

The ArenaController owns all orchestration logic per ARCHITECTURE.md.
It manages round flow, calls agents in order, and collects responses.
Voting and elimination logic will be added in Phase 2.
"""

from ai_hunger_games.agents.agent import RoundContext
from ai_hunger_games.agents.registry import AgentRegistry
from ai_hunger_games.arena.elimination import (
    EliminationCandidate,
    EliminationResult,
    determine_elimination,
)
from ai_hunger_games.arena.round_state import RoundState
from ai_hunger_games.core.config import Settings
from ai_hunger_games.core.logging_setup import get_logger
from ai_hunger_games.voting import aggregate_votes, collect_votes
from ai_hunger_games.voting.types import VotingRoundResult


logger = get_logger(__name__)


class InsufficientAgentsError(Exception):
    """Raised when there are not enough agents to run a round."""
    
    pass


class ArenaController:
    """Controls round flow and agent orchestration.
    
    The arena engine owns all orchestration logic. It calls agents
    in order and collects responses. Per ARCHITECTURE.md, it does
    NOT generate LLM prompts directly - that's the agent's job.
    """
    
    MINIMUM_AGENTS = 3
    
    def __init__(self, registry: AgentRegistry, settings: Settings) -> None:
        """Initialize the arena controller.
        
        Args:
            registry: The agent registry containing active agents.
            settings: Configuration settings for the arena.
        """
        self._registry = registry
        self._settings = settings
        self._current_round = 0
        self._round_history: list[RoundState] = []
        self._voting_history: list[VotingRoundResult] = []
        self._cumulative_votes: dict[str, int] = {}
        
        logger.info(
            f"ArenaController initialized with {registry.count()} agents"
        )
    
    @property
    def current_round(self) -> int:
        """Get the current round number."""
        return self._current_round
    
    @property
    def agent_count(self) -> int:
        """Get the number of active agents."""
        return self._registry.count()
    
    def start_round(self, prompt: str) -> RoundState:
        """Start a new round and collect responses from all agents.
        
        Args:
            prompt: The prompt to send to all agents.
        
        Returns:
            The completed RoundState with all responses.
        
        Raises:
            InsufficientAgentsError: If fewer than minimum agents exist.
        """
        if self._registry.count() < self.MINIMUM_AGENTS:
            raise InsufficientAgentsError(
                f"Need at least {self.MINIMUM_AGENTS} agents, "
                f"but only {self._registry.count()} registered"
            )
        
        self._current_round += 1
        
        logger.info(
            f"Starting round {self._current_round} with prompt: "
            f"'{prompt[:50]}...'"
        )
        
        round_state = RoundState(
            round_number=self._current_round,
            prompt=prompt
        )
        
        round_state = self._collect_responses(round_state)
        
        round_state.is_complete = True
        self._round_history.append(round_state)
        
        logger.info(
            f"Round {self._current_round} complete with "
            f"{round_state.response_count()} responses"
        )
        
        return round_state
    
    def _collect_responses(self, round_state: RoundState) -> RoundState:
        """Collect responses from all agents.
        
        Args:
            round_state: The round state to populate.
        
        Returns:
            Updated round state with responses.
        """
        context = RoundContext(
            round_number=round_state.round_number,
            prompt=round_state.prompt
        )
        
        for agent in self._registry:
            logger.debug(f"Collecting response from agent '{agent.agent_id}'")
            
            response = agent.generate_response(context)
            round_state.add_response(agent.agent_id, response)
        
        return round_state
    
    def conduct_voting(
        self,
        round_state: RoundState,
        vote_choices: dict[str, str]
    ) -> VotingRoundResult:
        """Conduct voting for a completed round.
        
        Args:
            round_state: The completed round state.
            vote_choices: Mapping of voter_id to voted_for_id.
        
        Returns:
            Aggregated voting results.
        """
        votes = collect_votes(round_state, vote_choices)
        
        agent_ids = [resp.agent_id for resp in round_state.responses]
        result = aggregate_votes(votes, round_state.round_number, agent_ids)
        
        self._update_cumulative_votes(result)
        self._voting_history.append(result)
        
        logger.info(
            f"Voting complete for round {round_state.round_number}: "
            f"{len(votes)} votes cast"
        )
        
        return result
    
    def _update_cumulative_votes(self, result: VotingRoundResult) -> None:
        """Update cumulative vote counts."""
        for vote_result in result.results:
            if vote_result.agent_id not in self._cumulative_votes:
                self._cumulative_votes[vote_result.agent_id] = 0
            self._cumulative_votes[vote_result.agent_id] += (
                vote_result.votes_received
            )
    
    def determine_elimination_candidate(
        self
    ) -> EliminationResult:
        """Determine which agent should be eliminated.
        
        Uses cumulative votes and historical averages for tie-breaking.
        
        Returns:
            Elimination result with selected agent.
        """
        if not self._voting_history:
            raise ValueError(
                "Cannot determine elimination without voting history"
            )
        
        candidates = self._build_elimination_candidates()
        result = determine_elimination(candidates, self._settings.random_seed)
        
        logger.info(
            f"Elimination determined: '{result.eliminated_agent_id}' "
            f"with {result.cumulative_votes} votes"
        )
        
        return result
    
    def _build_elimination_candidates(
        self
    ) -> list[EliminationCandidate]:
        """Build elimination candidates with scores."""
        candidates = []
        
        for agent_id in self._registry.get_ids():
            cumulative = self._cumulative_votes.get(agent_id, 0)
            avg = self._calculate_historical_average(agent_id)
            
            candidates.append(
                EliminationCandidate(
                    agent_id=agent_id,
                    cumulative_votes=cumulative,
                    historical_average=avg
                )
            )
        
        return candidates
    
    def _calculate_historical_average(self, agent_id: str) -> float:
        """Calculate historical vote average for an agent."""
        if not self._voting_history:
            return 0.0
        
        total_votes = sum(
            result.get_votes_for(agent_id)
            for result in self._voting_history
        )
        
        return total_votes / len(self._voting_history)
    
    def get_round_history(self) -> list[RoundState]:
        """Get the history of all completed rounds.
        
        Returns:
            List of all round states in order.
        """
        return list(self._round_history)
    
    def get_round(self, round_number: int) -> RoundState | None:
        """Get a specific round by number.
        
        Args:
            round_number: The round number (1-indexed).
        
        Returns:
            The round state or None if not found.
        """
        for round_state in self._round_history:
            if round_state.round_number == round_number:
                return round_state
        return None
