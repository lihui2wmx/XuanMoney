# XuanMoney Development Rules

This repository is the source of truth for implementation decisions. AI agents must be able to resume work from repository state without relying on prior chat history.

## Mandatory read order for AI handoff

1. `AGENTS.md`
2. `docs/HANDOFF.md`
3. `docs/AI_WORKFLOW.md`
4. `docs/ARCHITECTURE.md`
5. `docs/TOOLS.md`
6. the relevant section of `docs/DEVELOPMENT_LOG.md`
7. implementation and tests touched by the active bounded increment

## Working model

1. Read the repository state before proposing or implementing a change.
2. Work in bounded increments on feature branches; do not develop directly on `main`.
3. Keep financial domain logic separate from LLM orchestration.
4. Every deterministic financial rule belongs in `src/xuanmoney/finance/` and must be testable without an LLM.
5. Material agent conclusions must carry evidence that identifies source fields, periods, dimensions/members when applicable, and available provenance.
6. The project remains read-only. Do not add payment, posting, filing, deletion, unrestricted SQL, or other financial write actions without an explicit milestone change.
7. Do not let an LLM silently define accounting formulas, metric semantics, permissions, validation rules, unknown spreadsheet mappings, or business dimensions.
8. Any new metric, semantic mapping rule, validator, or model-callable tool requires tests covering normal and edge cases.
9. Prefer explicit state transitions and typed models over open-ended autonomous loops.
10. Fail closed on ambiguous financial semantics. Unknown data must not be guessed into canonical finance fields.
11. Record milestone-level changes in `docs/DEVELOPMENT_LOG.md`.
12. Refresh `docs/HANDOFF.md` before ending a meaningful development session.
13. Core GitHub Actions CI must use GitHub-hosted runners; do not use `self-hosted`. Prefer GitHub-maintained actions for checkout and runtime setup.
14. A failing test or CI run is unfinished work, not a handoff state to describe as complete.
15. Do not describe deterministic accounting decomposition or dimensional contribution analysis as causal root-cause analysis unless a separate causal method is explicitly implemented and validated.
16. Do not combine multiple business dimensions into an implicit cube unless the active milestone explicitly introduces and validates that behavior.
17. A future model may invoke only tools explicitly present in the controlled model-callable registry. Tool failure does not authorize fallback to SQL, Python, filesystem access, or unregistered code paths.
18. Do not add a public runtime `register()` mechanism or dynamic import path to the model-callable tool registry.
19. Application-owned ingestion paths are not model-callable until a separate file-access policy is implemented and reviewed.

## Current milestone

`Controlled Analysis Tools v0.1`: a fixed, typed, read-only model-callable registry over the existing deterministic financial and one-dimensional analysis services.

## Exit conditions for the current milestone

- the model-callable registry exposes a fixed code-reviewed tool set with no public dynamic-registration API;
- current model-callable tools are limited to `analyze_financials` and `analyze_dimension`;
- every tool is classified `read_only`;
- every tool has explicit Pydantic request and response schemas;
- JSON Schema metadata is available for future model adapters;
- unknown tool names fail closed;
- unknown top-level request parameters fail closed;
- request validation errors omit raw input values from structured error details;
- domain/service failures normalize to a stable tool failure contract;
- handler responses are validated against the declared response model;
- filesystem loaders, SQL, Python execution, dynamic imports, and financial writes are absent from the model-callable registry;
- tests verify the registry, schemas, successful invocations, unknown-tool behavior, validation behavior, and execution failures;
- CI passes on a GitHub-hosted runner;
- `docs/TOOLS.md`, architecture, development log, and canonical handoff reflect the implemented and verified state.

## Canonical next action

Always use `docs/HANDOFF.md` for the single recommended next bounded increment. Do not infer the next action from stale chat context.
