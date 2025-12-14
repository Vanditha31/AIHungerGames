# Project Overview
AI Hunger Games is a local, multi-agent LLM arena where multiple language models with distinct personalities answer the same prompt, vote on each other's responses, and are eliminated over successive rounds. Eliminated agents are replaced by newly generated personalities, enabling emergent social, strategic, and evolutionary behaviors.

## Goal
- Observe emergent multi-agent behaviors such as persuasion, alliance formation, collusion, sabotage, and strategic voting
- Create a repeatable experimental framework for studying LLM social dynamics

Target users:
- AI engineers
- Researchers experimenting with multi-agent systems
- Advanced hobbyists running local LLM experiments

## Non-Goals
- This is NOT a general-purpose chatbot framework
- This is NOT a production SaaS platform
- This is NOT focused on fine-tuning models
- This does NOT allow agents to access external tools, the internet, or the file system
- This does NOT aim to optimize answer correctness over emergent behavior
- No user-provided personalities in MVP
- No HTTP API in MVP (CLI only)
- No inheritance-based personality evolution in MVP
- No bit-for-bit deterministic LLM output (best-effort reproducibility only)

## Constraints
- Languages: Python 3.11 only
- LLM runtime: Ollama (local models only)
- LLM model: Single base model for all agents (default: llama3.1:8b)
- No cloud dependencies required for core functionality
- No agent-to-agent direct messaging in MVP
- Deterministic execution preferred where possible (best-effort)
- All agent behavior must be explainable via logs
- Fixed temperature (default 0.2) for reproducibility
- Fixed random seed for personality generation
- Configuration via single file: config/settings.yaml
- CLI flags override config; environment variables only for secrets

## Success Criteria
- 8 agents can complete at least 10 full rounds without crashing
- Voting results and eliminations are reproducible given the same seed
- Agents exhibit divergent voting patterns over time
- Eliminations occur based on measurable signals (cumulative votes against), not randomness alone
- Exactly one agent eliminated every N rounds (default: every 2 rounds)
- Unit tests cover arena logic, voting aggregation, and elimination rules
- Ollama layer is mocked by default in tests
- One optional integration test behind a flag
