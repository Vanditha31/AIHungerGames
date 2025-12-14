# Architecture

## High-Level Architecture (Textual)

- API Layer
  - CLI only (no HTTP in MVP)
  - Accepts user prompts
  - Displays round results (plain text summary)
  - Optional JSON dump for logs

- Arena Engine (Core)
  - Agent lifecycle management
  - Round orchestration
  - Voting and elimination logic
  - Minimum agents: 3
  - Start: 8 agents
  - Eliminate 1 every 2 rounds (configurable via rounds_per_elimination)

- Agent Layer
  - Personality prompts (generated from fixed template + random seed)
  - Memory management (sliding window of last N rounds, default: 5)
  - Response generation
  - Prompts stored in prompts/ directory (versioned, immutable once used)

- Voting Module
  - Single-choice voting (each agent votes for one answer, not their own)
  - Self-voting is forbidden
  - Tie handling: lowest historical vote average, then fixed random seed

- Evolution Module
  - New personalities generated from same template + new random seed
  - No inheritance in MVP
  - Post-mortem analysis is observational only (stored as metadata)

- Persistence Layer
  - Round logs
  - Votes
  - Eliminations
  - Personality history

- Configuration
  - Single config file: config/settings.yaml
  - CLI flags override config
  - Environment variables only for secrets
  - Required config: model_name, num_agents, rounds_per_elimination, temperature, random_seed

## Key Design Decisions

- Local-first (Ollama) to enable offline experimentation
- Single base model for all agents (default: llama3.1:8b) to eliminate model capability as confounding variable
- Agents are stateless models + stateful wrappers
- Arena engine owns all orchestration logic
- Agents never know other agents' identities directly
- Evolution is driven by elimination, not parameter tuning
- Best-effort reproducibility via fixed temperature (0.2) and random seed
- Full logging of prompts + outputs for auditability

## Round Structure

A round consists of:
1. User Prompt delivered to all agents
2. All agents generate responses
3. All agents vote (single-choice, cannot vote for self)
4. Scores updated (cumulative votes received against each agent)
5. Elimination only after N rounds (configurable)

## Personality System

Personality structure (MVP):
- Communication style: concise | verbose | rhetorical | analytical
- Ethical stance: strict | flexible | amoral
- Social strategy: cooperative | opportunistic | adversarial
- Risk tolerance: low | medium | high

These are categorical labels, not free-form prose.

Variation policy:
- High variation at initialization
- Very small mutations during evolution

## Memory Management

Agents have read-only access to:
- Their own previous answers
- Their own previous votes
- Aggregate voting outcomes (counts only, no identities)

Memory policy:
- Sliding window of last N rounds (default: 5)
- No long-term memory in MVP
- No summarization yet

## Prompt Management

Prompts live in a dedicated directory:
```
prompts/
├── answer_prompt_v1.md
├── voting_prompt_v1.md
└── personality_prompt_v1.md
```

Rules:
- Prompts are immutable once used in a run
- Any prompt change = new versioned file
- Prompt filename is logged per round

## Module Responsibilities

- arena/
  - Controls round flow
  - Calls agents in correct order
  - Applies scoring and elimination rules
  - Implements elimination: exactly 1 agent every N rounds
  - Elimination score = cumulative votes received against the agent
  - Does NOT generate LLM prompts directly

- agents/
  - Defines Agent abstraction
  - Manages personality, memory, and voting prompts
  - Loads prompts from prompts/ directory
  - Does NOT control round flow

- voting/
  - Implements single-choice voting
  - Aggregates votes
  - Enforces self-voting prohibition
  - Handles ties deterministically (lowest historical avg, then seed)
  - Does NOT eliminate agents

- evolution/
  - Generates new personalities from template + new seed
  - Performs post-mortem analysis (observational, stored as metadata)
  - No inheritance in MVP
  - Does NOT interact with Ollama directly

- storage/
  - Read/write arena state
  - Logging and persistence only
  - No business logic

## Forbidden Patterns

- No business logic in API or CLI handlers
- No direct Ollama calls outside the Agent layer
- No agent accessing global arena state directly
- No persistence logic outside storage/
- No circular dependencies between modules
- No storing other agents' full responses in agent memory
- No cross-agent memory sharing
