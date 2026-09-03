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
8. `docs/PROVIDER_SAFETY.md`
9. `docs/CREDENTIALS.md`
10. the relevant section of `docs/DEVELOPMENT_LOG.md`
11. implementation and tests touched by the active bounded increment

## Working model

1. Read the repository state before proposing or implementing a change.
2. Work in bounded increments on feature branches; do not develop directly on `main`.
3. Keep financial domain logic separate from LLM orchestration.
4. Every deterministic financial rule belongs in `src/xuanmoney/finance/` and must be testable without an LLM.
5. Material agent conclusions must carry evidence that identifies source fields, periods, dimensions/members when applicable, and available provenance.
6. The project remains read-only. Do not add payment, posting, filing, deletion, unrestricted SQL, or other financial write actions without an explicit milestone change.
7. Do not let an LLM silently define accounting formulas, metric semantics, permissions, validation rules, unknown spreadsheet mappings, or business dimensions.
8. Any new metric, semantic mapping rule, validator, model-callable tool, runtime transition, provider boundary, provider bridge, provider configuration contract, provider failure contract, or credential-resolution boundary requires tests covering normal and edge cases.
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
22. `BoundedModelRuntime` depends on the existing `ModelPort`. Lower-level provider transport must remain behind an explicit, tested `ModelPort` bridge.
23. The provider bridge may translate typed runtime requests and decode provider transport responses, but runtime-owned validation of planner/synthesis semantics must not migrate into the bridge.
24. `xuanmoney.model` is the lower-level provider transport package and must not depend on `xuanmoney.runtime`; runtime-owned bridge code may depend downward on `xuanmoney.model`.
25. Provider configuration must not serialize, log, or embed secret credential values. Credential objects are references only; secret resolution remains application-owned.
26. Provider request timeout must be bounded and automatic provider retries remain disabled (`max_attempts = 1`) unless a future milestone explicitly changes and validates the runtime policy.
27. Public provider failure objects must contain only stable failure codes and code-derived safe messages; raw provider diagnostics, exception text, HTTP bodies, request payloads, and credential material must not enter serialized failures.
28. Credential resolution must remain outside model-callable surfaces. Any resolved secret wrapper must redact representation/serialization and must not be stored in `ProviderConfiguration`, `ModelRequest`, runtime results, evidence, or logs.
29. `xuanmoney.credentials` is an application-owned credential boundary. It may depend on model-layer credential references; `xuanmoney.model`, runtime, tools, and finance code must not depend on resolved secret values.
30. Revealing a protected credential is an explicit trusted-boundary operation. Do not reveal a secret for diagnostics, validation messages, logging, evidence, prompt/model context, or test snapshots.
31. `ModelRequest.context` and `ModelResponse.metadata` must remain strict JSON-safe transport envelopes; arbitrary Python objects and non-standard JSON numeric constants must fail closed without exposing invalid input values in validation diagnostics.
32. Concrete credential resolvers must use application-owned composition inputs. The environment resolver receives an injected `Mapping[str, str]`; credential resolution code must not give model/runtime/tool/finance layers direct environment access or expose the backing mapping through representation/errors.

## Current milestone

`Environment Credential Resolver v0.1`: **ACTIVE**.

This milestone implements the first concrete application-owned `CredentialResolver` for existing `CredentialSource.ENVIRONMENT` references. Resolution is driven by an injected mapping, returns only `ProtectedSecret`, and preserves sanitized failure behavior without making process environment access part of model/runtime code.

## Exit conditions for the current milestone

- concrete `EnvironmentCredentialResolver` implements the existing credential resolver protocol;
- constructor accepts an injected `Mapping[str, str]` and performs no implicit process-environment lookup;
- present non-empty environment references resolve to `ProtectedSecret`;
- missing, empty, invalid-type, mapping-lookup failure, and unsupported-source cases fail closed through existing sanitized credential-resolution errors;
- resolver representation does not expose the backing mapping or credential values;
- failure objects retain no reference identifier, secret value, raw mapping diagnostic, cause, or context chain;
- deterministic tests do not depend on the host process environment;
- `ProtectedSecret`, strict JSON-safe model transport, `max_attempts = 1`, package direction, and bounded runtime invariants remain unchanged;
- no provider SDK, provider network call, retry/backoff, fallback, streaming, new tool, or financial-write path is introduced;
- CI passes on the official GitHub-hosted runner;
- `docs/CREDENTIALS.md`, development log, and canonical handoff reflect the reviewed state.

## Canonical next action

Always use `docs/HANDOFF.md` for the single recommended next bounded increment. Do not infer the next action from stale chat context.
