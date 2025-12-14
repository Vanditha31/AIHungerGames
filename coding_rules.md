# Coding Rules

## General
- Explicit is better than implicit
- Readability > cleverness
- Deterministic behavior preferred

## Functions
- Max 30 lines per function
- Single responsibility only
- Must return explicit values (no hidden side effects)

## Classes
- One clear responsibility per class
- No "manager" or "helper" god classes
- Constructor must not perform heavy logic

## Typing
- Use Python type hints everywhere
- No use of Any unless explicitly justified
- Typed dictionaries or dataclasses preferred

## Documentation
- All public classes and methods require docstrings
- Docstrings must explain WHY, not just WHAT

## Error Handling
- No silent failures
- All exceptions must be logged or surfaced
- Fail fast on invalid arena states

## LLM Interaction
- All prompts must be versioned and logged
- No inline prompt strings scattered in code
- Prompt changes require explicit commit
- Prompts live in prompts/ directory (e.g., answer_prompt_v1.md)
- Prompts are immutable once used in a run
- Any prompt change = new versioned file
- Prompt filename is logged per round

## Voting Rules
- Self-voting is explicitly forbidden
- Each agent votes for exactly one answer that is not their own
- Ties are broken deterministically: lowest historical vote average, then fixed random seed

## Testing Strategy
- Unit tests required for:
  - Arena logic
  - Voting aggregation
  - Elimination rules
- Ollama layer is mocked by default
- One optional integration test behind a flag (e.g., --integration)
- Tests must be deterministic given fixed seeds

If a rule is not written here, assume it is NOT allowed.
