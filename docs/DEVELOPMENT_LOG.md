# Development Log

## 2026-09-02 — Project bootstrap

Status: **COMPLETE**

Established the repository baseline and the first deterministic, read-only finance-analysis slice:

- typed income statement and balance sheet contracts using `Decimal`;
- evidence-bearing metric/finding models;
- profitability metrics and period variance;
- balance-sheet accounting identity validation;
- bounded agent state and service workflow;
- core unit tests and GitHub Actions CI.

## 2026-09-02 — Normalized tabular ingestion and AI handoff workflow

Status: **COMPLETE**

Added explicit semantic aliases, fail-closed CSV/XLSX ingestion, deterministic decimal parsing, provenance, repository-native AI handoff, contribution guidance, and hardened GitHub-hosted CI.

## 2026-09-02 — Profit Bridge v0.1

Status: **COMPLETE — merged via PR #1**

Added deterministic net-profit change decomposition with exact `Decimal` reconciliation, validation, provenance, and service-level tests. PR #1 also established Apache License 2.0 licensing and was squash-merged to `main` at `d65aeda6f0e22319768d0a8213f8c73fd7436eec`.

## 2026-09-02 — Dimensional Analysis v0.1

Status: **COMPLETE — merged via PR #3**

Added explicit one-dimensional ingestion, deterministic member aggregation, member revenue/COGS/gross-profit/gross-margin metrics, new/disappearing member comparison, exact contribution reconciliation, provenance, mixed-currency fail-closed behavior, and `analyze_dimension`. PR #3 was squash-merged to `main` at `6e7334c3fbd576c7f6657ca8f5b70a6a0ceb193c` after successful GitHub-hosted CI.

## 2026-09-02 — Controlled Analysis Tools v0.1

Status: **COMPLETE — merged via PR #4**

Implemented the fixed read-only model-callable boundary:

- immutable `AnalysisToolRegistry` without a public dynamic `register()` API;
- model-callable tools limited to `analyze_financials` and `analyze_dimension`;
- enforced `ToolRisk.READ_ONLY`;
- Pydantic request/response contracts and JSON Schema metadata;
- `extra="forbid"` request envelopes;
- stable tool failures for unknown tool, invalid request, execution failure, and invalid response;
- raw request input omitted from structured validation errors;
- service/domain failures normalized through `ToolInvocationError` / `ToolFailure`;
- filesystem loaders, SQL, Python/shell execution, dynamic imports, and financial writes excluded from the model-callable surface;
- `docs/TOOLS.md` documenting the trust boundary.

Final push and PR checks passed on GitHub-hosted `ubuntu-latest`. PR #4 was squash-merged to `main` at `9934248ade818b66ff14f385ee8063f0791ce837`.

## 2026-09-02 — Bounded Model Runtime v0.1

Status: **COMPLETE — merged via PR #5**

Implemented:

- provider-independent `ModelPort` with separate `plan` and `synthesize` methods;
- typed `PlanningRequest`, `PlannerDecision`, `ToolCallPlan`, `NoToolPlan`, `SynthesisRequest`, and `SynthesisOutput` contracts;
- `BoundedModelRuntime` enforcing one plan, at most one registered tool invocation, and one synthesis;
- fail-closed unknown-tool behavior through the existing controlled registry;
- terminal behavior for invalid arguments, tool execution failure, planner failure, and synthesis failure;
- no retry loop, ReAct loop, SQL/Python fallback, filesystem fallback, or alternate execution path;
- provider exception normalization that does not expose provider exception text in runtime results;
- whitespace-only planner reasons and synthesis answers rejected;
- deterministic fake-model tests for successful flow and major failure paths;
- `docs/RUNTIME.md` defining the runtime/model trust boundary.

PR #5 passed GitHub-hosted CI and was squash-merged to `main` at `d3fb61a789e70f2e4029605462a294543e6fdc39`.

### Runtime invariant

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

No external LLM/provider SDK was added.

## 2026-09-02 — Model Provider Contract v0.1

Status: **COMPLETE — merged via PR #6**

Implemented:

- typed `ModelRequest` and `ModelResponse` contracts with `extra="forbid"`;
- provider-neutral `ModelProvider.complete(ModelRequest) -> ModelResponse` protocol;
- `BaseModelAdapter` provider implementation boundary;
- deterministic `EchoModelAdapter` used only for tests;
- contract tests for typed request/response behavior and forbidden extra fields;
- explicit separation between the runtime-facing `ModelPort` and lower-level `ModelProvider` transport contract;
- provider-boundary documentation;
- no vendor SDK, credentials, external network call, streaming, function calling, financial tool access, or financial write path.

Final PR head `6e204f11fee6a887580b9b4b06d2538831c6bbe8` passed GitHub-hosted PR CI #130. PR #6 was squash-merged to `main` at `c8f18f93b72cd0f4462e0f94a2cbbaebcdafa305`.

## 2026-09-02 — ModelPort Provider Bridge v0.1

Status: **COMPLETE — merged via PR #8**

Implemented:

- runtime-owned `ModelPortProviderBridge` implementing `ModelPort.plan()` and `ModelPort.synthesize()` over an injected lower-level `ModelProvider`;
- provider-neutral phase translation for typed `PlanningRequest` and `SynthesisRequest` values;
- copied response JSON Schema included in each transport request;
- exactly one `ModelProvider.complete()` call for each reached phase;
- strict JSON decoding of `ModelResponse.content`, including rejection of malformed JSON and non-standard `NaN`/`Infinity` constants;
- planner/synthesis semantic validation remains in `BoundedModelRuntime`;
- complete `BoundedModelRuntime` execution through a deterministic fake provider;
- terminal no-retry behavior for malformed transport data and provider exceptions;
- provider exception diagnostics remain sanitized by the existing runtime boundary;
- package dependency direction enforced as `xuanmoney.runtime -> xuanmoney.model`, never the reverse;
- no changes to Finance Kernel, controlled Tool Registry, runtime execution sequence, or financial write boundary.

Integration review found and corrected the initial package-layering inversion before merge. The corrected bridge lives in `xuanmoney.runtime.provider_bridge`, while `xuanmoney.model` remains transport-only.

Final branch head `427b9083b206fa8abb7b97d9cb1f3b558c957f2d` passed PR CI #181. Final integration review found no remaining blocker, and PR #8 was squash-merged to `main` at `b6614b7f207fe6d594c8472758a053c85668bae6`.

### Preserved boundary

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge
        -> ModelProvider
        -> provider adapter
```

## 2026-09-03 — Provider Configuration & Safety Contract v0.1

Status: **COMPLETE — merged via PR #10**

Implemented immutable non-secret provider configuration, bounded timeout, `max_attempts=1`, credential references, strict failure taxonomy, safe code-derived public messages, deterministic safety tests, and `docs/PROVIDER_SAFETY.md`.

Final PR head `93f2d2b8202cb55db31e82efbad11d61f9d78d4c` passed GitHub-hosted PR CI #218 and PR #10 was squash-merged to `main` at `0148962739a80cdb53c25dbbf445dc9584a75a4a`.

## 2026-09-03 — Credential Resolver Boundary v0.1

Status: **COMPLETE — merged via PR #12**

Implemented `CredentialResolver`, runtime-only `ProtectedSecret`, safe credential failure contracts, transport JSON-safety hardening, and credential documentation. Final head `3640269d2e47551c77bce97e9b8fbccfd4714d54` passed PR CI #248; PR #12 was squash-merged at `84edd3e90c9c5c2551e5314410bd7eb554cfe75e`.

## 2026-09-03 — Environment Credential Resolver v0.1

Status: **COMPLETE — merged via PR #14**

Implemented injected-mapping `EnvironmentCredentialResolver` with sanitized failures and redacted representation. Final head `7646a1d38e105aeb844bba01a96dc0395988273d` passed PR CI #269; PR #14 was squash-merged at `67c957eb199efc8ee8b7c8955635e667237b58f7`.

## 2026-09-03 — Provider Adapter Credential Injection v0.1

Status: **COMPLETE — merged via PR #16**

Implemented application-owned provider composition, trusted factory boundary, credential resolution/reveal confinement, sanitized construction failures, and deterministic bridge/runtime integration coverage. Final head `9c1e5dbc47931c5cc0720811a3c5799e7a575fca` passed PR CI #298; PR #16 was squash-merged at `572ac05873ba3ff3cebd182fc72d07bb2f2dec65`.

## 2026-09-03 — Controlled Provider Factory Registry v0.1

Status: **COMPLETE — merged via PR #18**

Implemented immutable application-owned provider factory allowlist, normalized fail-closed provider selection, no public registration/dynamic discovery, credential-consuming registry/runtime integration coverage, and `docs/PROVIDER_REGISTRY.md`.

Final feature head `4cc6d621c9296cff5424ae13f95b0607a20cb931` passed PR CI #320; integration review `5096980951` found no blocker; PR #18 was squash-merged at `73f7cbb5ffeeeaa79204d5c38f12e2e1c47f6b56`.

## 2026-09-03 — First Real Provider Adapter v0.1 Readiness/Design

Status: **COMPLETE — merged via PR #20**

Selected OpenAI Responses API and the official Python SDK as the first real provider target. Defined the trusted construction boundary, timeout/no-retry policy, request/response translation, failure normalization, deterministic test strategy, and non-goals before implementation.

Final head `1d09f6c1e94c44d47883868be9c21f8dd781666f` passed PR CI #334; integration design review `5102812238` found no blocker; PR #20 was squash-merged at `f3c2cf66917a28a580ea16e4a28ae212de3753d9`.

## 2026-09-03 — OpenAI Provider Adapter v0.1

Status: **COMPLETE — merged via PR #22**

Implemented:

- bounded official dependency `openai>=3.7,<4`;
- application-owned `OpenAIProviderFactory` as the only OpenAI-specific trusted `ProtectedSecret.reveal()` boundary;
- synchronous `OpenAIProviderAdapter` implementing the existing `ModelProvider.complete(ModelRequest) -> ModelResponse` contract;
- SDK client construction with configured timeout and explicit `max_retries=0`;
- preservation of `ModelRequest(prompt, context)` via `prompt -> Responses instructions` and deterministic JSON-safe `context -> Responses input`;
- at most one synchronous `responses.create()` call per `complete()`;
- no provider-native tools, streaming, background responses, application retry/backoff, provider/model fallback, or alternate execution path;
- canonical nonblank `output_text` mapping to `ModelResponse(provider="openai")` and fail-closed `INVALID_RESPONSE` handling;
- stable normalization of authentication/permission, timeout, rate-limit, service, configuration, connection, and unexpected SDK failures without raw provider diagnostics or credential leakage;
- deterministic fake-SDK tests covering construction, request mapping, failure normalization, secret safety, and registry/composer/bridge/runtime integration;
- correction of the readiness-document mismatch that described nonexistent `ModelRequest.instructions/input` fields without changing lower-level model/runtime schemas.

Verification:

- implementation/test head `26d317d1398b717d15d468288db3dab866231c6c`: PR CI #346 success;
- documentation-synchronized head `564f8becdb06ffd6ea653e8281d5e8035707ffd8`: PR CI #350 success;
- development-log synchronized head `c21232783ee59bf932a545ca5507823ee234a0ff`: PR CI #352 success;
- final handoff head `318a10e565696cb492bce6d02d4a1c5843fb2bfe`: PR CI #354 success;
- final branch was `behind_by=0`, PR #22 was mergeable, and no review threads remained;
- integration review `5103040205` found no remaining code, architecture, provider-safety, dependency-direction, governance, or bounded-scope blocker;
- PR #22 was squash-merged to `main` at `40ddbf723fda8dad0ba8044286bd2a5c2ed3d072`.

No live provider network call, live credential CI, second provider, retry/backoff, fallback, streaming, background response mode, provider-native tools/function calling, secret-manager integration, runtime/finance/tool expansion, production API/UI, or financial write path was introduced.

### Next boundary

Start **Application Runtime Composition v0.1** as a separate bounded increment. Add one application-owned construction boundary that wires validated provider configuration, injected credential resolution, the fixed provider factory registry, `ModelPortProviderBridge`, the existing controlled analysis tool registry, and `BoundedModelRuntime` together. Keep deterministic tests network-free and preserve all no-retry/no-fallback/read-only/model-control boundaries.
