# XuanMoney Development Rules

This repository is the source of truth for implementation decisions. AI agents must be able to resume work from repository state without relying on prior chat history.

## Mandatory read order for AI handoff

1. `AGENTS.md`
2. `docs/HANDOFF.md`
3. `docs/AI_WORKFLOW.md`
4. `docs/ARCHITECTURE.md`
5. the relevant section of `docs/DEVELOPMENT_LOG.md`
6. implementation and tests touched by the active bounded increment

## Working model

1. Read the repository state before proposing or implementing a change.
2. Work in bounded increments on feature branches; do not develop directly on `main`.
3. Keep financial domain logic separate from LLM orchestration.
4. Every deterministic financial rule belongs in `src/xuanmoney/finance/` and must be testable without an LLM.
5. Material agent conclusions must carry evidence that identifies source fields, periods, and available provenance.
6. v0.1 is read-only. Do not add payment, posting, filing, deletion, unrestricted SQL, or other financial write actions.
7. Do not let an LLM silently define accounting formulas, metric semantics, permissions, validation rules, or unknown spreadsheet mappings.
8. Any new metric, semantic mapping rule, or validator requires tests covering normal and edge cases.
9. Prefer explicit state transitions and typed models over open-ended autonomous loops.
10. Fail closed on ambiguous financial semantics. Unknown data must not be guessed into canonical finance fields.
11. Record milestone-level changes in `docs/DEVELOPMENT_LOG.md`.
12. Refresh `docs/HANDOFF.md` before ending a meaningful development session.
13. Core GitHub Actions CI must use GitHub-hosted runners; do not use `self-hosted`. Prefer GitHub-maintained actions for checkout and runtime setup.
14. A failing test or CI run is unfinished work, not a handoff state to describe as complete.
15. Do not describe deterministic accounting decomposition as causal root-cause analysis unless a separate causal method is explicitly implemented and validated.

## Current milestone

`Finance Agent v0.1`: deterministic profitability analysis, normalized tabular ingestion, explicit semantic mapping, period variance, reconciled Profit Bridge, validation, evidence, and a bounded orchestration boundary.

## Exit conditions for v0.1

- deterministic core profitability metrics are implemented and tested;
- normalized CSV/XLSX ingestion has explicit semantic mapping and provenance;
- period comparison is implemented and tested;
- Profit Bridge line-item contribution reconciles exactly to net-profit change and is tested;
- at least one accounting identity validator is implemented and tested;
- findings/results are evidence-backed;
- the orchestration state cannot perform financial write actions;
- CI runs the unit test suite on a GitHub-hosted runner;
- architecture, development log, and canonical handoff reflect the implemented and verified state.

## Canonical next action

Always use `docs/HANDOFF.md` for the single recommended next bounded increment. Do not infer the next action from stale chat context.
