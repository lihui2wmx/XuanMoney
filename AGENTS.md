# XuanMoney Development Rules

This repository is the source of truth for implementation decisions. AI agents must be able to resume work from repository state without relying on prior chat history.

## Mandatory read order for AI handoff

1. `AGENTS.md`
2. `docs/HANDOFF.md`
3. `docs/AI_WORKFLOW.md`
4. `docs/ARCHITECTURE.md`
5. `docs/TOOLS.md`
6. `docs/RUNTIME.md`
7. `docs/PROVIDER_CONTRACT.md`
8. the relevant section of `docs/DEVELOPMENT_LOG.md`
9. implementation and tests touched by the active bounded increment

## Working model

1. Read the repository state before proposing or implementing a change.
2. Work in bounded increments on feature branches; do not develop directly on `main`.
3. Keep financial domain logic separate from LLM orchestration.
4. Every deterministic financial rule belongs in `src/xuanmoney/finance/` and must be testable without an LLM.
5. Material agent conclusions must carry evidence that identifies source fields, periods, dimensions/members when applicable, and available provenance.
6. The project remains read-only. Do not add payment, posting, filing, deletion, unrestricted SQL, or other financial write actions without an explicit milestone change.
7. Do not let an LLM silently define accounting formulas, metric semantics, permissions, validation rules, unknown spreadsheet mappings, or business dimensions.
8. Any new metric, semantic mapping rule, validator, model-callable tool, runtime transition, or provider boundary requires tests covering normal and edge cases.
9. Prefer explicit state transitions and typed models over open-ended autonomous loops.
10. Fail closed on ambiguous financial semantics. Unknown data must not be guessed into canonical finance fields.
11. Record milestone-level changes in `docs/DEVELOPMENT_LOG.md`.
12. Refresh `docs/HANDOFF.md` before ending a meaningful development session.
13. Core GitHub Actions CI must use GitHub-hosted runners; do not use `self-hosted`. Prefer GitHub-maintained actions for checkout and runtime setup.
14. A failing test or CI run is unfinished work, not a handoff state to describe as complete.
15. Do not describe deterministic accounting decomposition or dimensional contribution analysis as causal root-cause analysis unless a separate causal method is explicitly implemented and validated.
16. Do not combine multiple business dimensions into an implicit cube unless the active milestone explicitly introduces and validates that behavior.
17. A model may invoke only tools explicitly present in the controlled model-callable registry. Tool failure does not authorize fallback to SQL, Python, filesystem access, or unregistered code paths.
18. Do not add a public runtime `register()` mechanism or dynamic import path to the model-callable tool registry.
19. Application-owned ingestion paths are not model-callable until a separate file-access policy is implemented and reviewed.
20. The model runtime is bounded: one planning call, at most one registered tool invocation, and one synthesis call. No autonomous retry or ReAct loop is allowed in the current architecture.
21. Provider adapters translate model I/O only; they must not add hidden tools, hidden retries, financial rules, or alternate execution paths.
22. `BoundedModelRuntime` depends on the existing `ModelPort`. A lower-level `ModelProvider` contract must not be described as runtime-integrated until an explicit, tested `ModelPort` bridge exists.

## Current milestone

`Model Provider Contract v0.1`: a provider-neutral lower-level model transport contract beneath the existing runtime-facing `ModelPort`.

## Exit conditions for the current milestone

- typed `ModelRequest` and `ModelResponse` Pydantic contracts exist with `extra="forbid"`;
- a provider-neutral `ModelProvider.complete(ModelRequest) -> ModelResponse` protocol exists without vendor SDK dependency;
- a provider adapter boundary exists without financial tool access or alternate execution paths;
- deterministic fake/echo provider tests cover successful request/response behavior and unknown-field rejection;
- provider contract tests use typed requests and responses consistently;
- documentation explicitly distinguishes `ModelProvider` from the existing runtime-facing `ModelPort`;
- no claim is made that `BoundedModelRuntime` is wired to `ModelProvider` in this milestone;
- no external LLM/provider SDK, credentials, network calls, streaming, function calling, filesystem access, SQL/Python execution, dynamic tool registration, or financial write path is introduced;
- the existing bounded runtime invariant remains unchanged;
- CI passes on a GitHub-hosted runner;
- `docs/PROVIDER_CONTRACT.md`, development log, canonical handoff, and PR description reflect the implemented and verified state.

## Canonical next action

Always use `docs/HANDOFF.md` for the single recommended next bounded increment. Do not infer the next action from stale chat context.
