"""Arena controller for orchestrating rounds.

The ArenaController owns all orchestration logic per ARCHITECTURE.md.
It manages round flow, calls agents in order, and collects responses.
Voting and elimination logic will be added in Phase 2.
"""

from typing import Optional

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
from ai_hunger_games.evolution.replacement import AgentReplacementCoordinator
from ai_hunger_games.observability.logger import EventLogger
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
    
    def __init__(
        self,
        registry: AgentRegistry,
        settings: Settings,
        replacement_coordinator: Optional[AgentReplacementCoordinator] = None,
        event_logger: Optional[EventLogger] = None
    ) -> None:
        """Initialize the arena controller.
        
        Args:
            registry: The agent registry containing active agents.
            settings: Configuration settings for the arena.
            replacement_coordinator: Optional coordinator for agent replacement.
            event_logger: Optional event logger for observability.
        """
        self._registry = registry
        self._settings = settings
        self._replacement_coordinator = replacement_coordinator
        self._event_logger = event_logger
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
        
        # Emit round started event
        if self._event_logger:
            self._event_logger.log_round_started(
                round_number=self._current_round,
                prompt=prompt
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
            
            # Emit agent responded event
            if self._event_logger:
                self._event_logger.log_agent_responded(
                    round_number=round_state.round_number,
                    agent_id=agent.agent_id,
                    response=response
                )
        
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
        
        # Emit individual vote events
        if self._event_logger:
            for vote in votes:
                self._event_logger.log_vote_cast(
                    round_number=vote.round_number,
                    voter_id=vote.voter_id,
                    voted_for_id=vote.voted_for_id
                )
        
        agent_ids = [resp.agent_id for resp in round_state.responses]
        result = aggregate_votes(votes, round_state.round_number, agent_ids)
        
        # Emit vote summary event
        if self._event_logger:
            vote_counts = {
                vr.agent_id: vr.votes_received for vr in result.results
            }
            self._event_logger.log_vote_summary(
                round_number=round_state.round_number,
                vote_counts=vote_counts
            )
        
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
        
        # Emit elimination event
        if self._event_logger:
            self._event_logger.log_elimination_decided(
                round_number=self._current_round,
                eliminated_agent_id=result.eliminated_agent_id,
                cumulative_votes=result.cumulative_votes,
                was_tie=result.was_tie
            )
        
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
    
    def execute_replacement(
        self,
        elimination_result: EliminationResult
    ) -> None:
        """Execute agent replacement after elimination.
        
        If a replacement coordinator is configured, removes the eliminated
        agent and creates a replacement with a fresh personality.
        
        Args:
            elimination_result: The elimination decision.
        """
        if not self._replacement_coordinator:
            logger.warning(
                "No replacement coordinator configured, "
                "eliminated agent will not be replaced"
            )
            return
        
        agent_id = elimination_result.eliminated_agent_id
        rounds_survived = self._current_round
        
        # Get old agent for logging before replacement
        if self._event_logger:
            old_agent = self._registry.get(agent_id)
            old_personality_dict = old_agent.personality.to_dict()
        
        self._replacement_coordinator.replace_agent(
            eliminated_agent_id=agent_id,
            rounds_survived=rounds_survived,
            total_votes_received=elimination_result.cumulative_votes,
            elimination_round=self._current_round,
            was_tie=elimination_result.was_tie
        )
        
        # Emit replacement event
        if self._event_logger:
            new_agent = self._registry.get(agent_id)
            new_personality_dict = new_agent.personality.to_dict()
            
            self._event_logger.log_agent_replaced(
                round_number=self._current_round,
                agent_id=agent_id,
                old_personality=old_personality_dict,
                new_personality=new_personality_dict
            )
        
        logger.info(
            f"Agent replacement executed for '{agent_id}' "
            f"after {rounds_survived} rounds"
        )
    
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
