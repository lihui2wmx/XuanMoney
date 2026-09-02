# XuanMoney Development Rules

This repository is the source of truth for implementation decisions. AI agents must be able to resume work from repository state without relying on prior chat history.

## Mandatory read order for AI handoff

1. `AGENTS.md`
2. `docs/HANDOFF.md`
3. `docs/AI_WORKFLOW.md`
4. `docs/ARCHITECTURE.md`
5. `docs/TOOLS.md`
6. `docs/RUNTIME.md`
7. the relevant section of `docs/DEVELOPMENT_LOG.md`
8. implementation and tests touched by the active bounded increment

## Working model

1. Read the repository state before proposing or implementing a change.
2. Work in bounded increments on feature branches; do not develop directly on `main`.
3. Keep financial domain logic separate from LLM orchestration.
4. Every deterministic financial rule belongs in `src/xuanmoney/finance/` and must be testable without an LLM.
5. Material agent conclusions must carry evidence that identifies source fields, periods, dimensions/members when applicable, and available provenance.
6. The project remains read-only. Do not add payment, posting, filing, deletion, unrestricted SQL, or other financial write actions without an explicit milestone change.
7. Do not let an LLM silently define accounting formulas, metric semantics, permissions, validation rules, unknown spreadsheet mappings, or business dimensions.
8. Any new metric, semantic mapping rule, validator, model-callable tool, or runtime transition requires tests covering normal and edge cases.
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
20. The model runtime is bounded: one planning call, at most one registered tool invocation, and one synthesis call. No autonomous retry or ReAct loop is allowed in the current milestone.
21. Provider adapters translate model I/O only; they must not add hidden tools, hidden retries, financial rules, or alternate execution paths.

## Current milestone

`Bounded Model Runtime v0.1`: a provider-independent, single-step planner/tool/synthesizer runtime over the controlled read-only analysis registry.

## Exit conditions for the current milestone

- a provider-independent `ModelPort` exists with no vendor SDK dependency;
- planning and synthesis use typed Pydantic contracts with `extra="forbid"`;
- planner output permits either `no_tool` or at most one tool call;
- the selected tool is enforced against `AnalysisToolRegistry`;
- tool arguments are validated by the existing tool request schemas;
- tool failure terminates the run without retry or fallback;
- synthesis occurs only after a successful validated tool result;
- planner/provider exceptions and synthesis/provider exceptions normalize to stable runtime failures without echoing provider exception text;
- blank/whitespace-only planner reasons and synthesis answers fail validation;
- deterministic fake-model tests cover complete, no-tool, unknown-tool, invalid-argument, execution-failure, invalid-plan, planner-exception, invalid-synthesis, and synthesis-exception paths;
- no external LLM/provider SDK, filesystem access, SQL/Python execution, dynamic tool registration, or financial write path is introduced;
- CI passes on a GitHub-hosted runner;
- `docs/RUNTIME.md`, development log, and canonical handoff reflect the implemented and verified state.

## Canonical next action

Always use `docs/HANDOFF.md` for the single recommended next bounded increment. Do not infer the next action from stale chat context.
