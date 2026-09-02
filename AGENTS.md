# XuanMoney Development Rules

This repository is the source of truth for implementation decisions.

## Working model

1. Read the repository state before proposing or implementing a change.
2. Work in bounded increments on feature branches; do not develop directly on `main`.
3. Keep financial domain logic separate from LLM orchestration.
4. Every deterministic financial rule belongs in `src/xuanmoney/finance/` and must be testable without an LLM.
5. Material agent conclusions must carry evidence that identifies their source fields and periods.
6. v0.1 is read-only. Do not add payment, posting, filing, deletion, unrestricted SQL, or other financial write actions.
7. Do not let an LLM silently define accounting formulas, metric semantics, permissions, or validation rules.
8. Any new metric or validator requires tests covering normal and edge cases.
9. Prefer explicit state transitions and typed models over open-ended autonomous loops.
10. Record milestone-level changes in `docs/DEVELOPMENT_LOG.md`.

## Current milestone

`Finance Agent v0.1`: deterministic profitability analysis, period variance, validation, evidence, and a bounded orchestration boundary.

## Exit conditions for v0.1

- deterministic core profitability metrics are implemented and tested;
- period comparison is implemented and tested;
- at least one accounting identity validator is implemented and tested;
- findings are evidence-backed;
- the orchestration state cannot perform financial write actions;
- CI runs the unit test suite;
- architecture and development log reflect the implemented state.
