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

Integration review corrected an early architectural-documentation mismatch that had implied direct `BoundedModelRuntime -> ModelProvider` integration. The final design records the intended layering as:

```text
BoundedModelRuntime
        -> ModelPort
        -> future bounded ModelPort/provider bridge
        -> ModelProvider
        -> provider adapter
        -> external model service
```

Final PR head `6e204f11fee6a887580b9b4b06d2538831c6bbe8` passed GitHub-hosted PR CI #130. PR #6 was squash-merged to `main` at `c8f18f93b72cd0f4462e0f94a2cbbaebcdafa305`.

### Next boundary

The next bounded implementation should be a provider-independent `ModelPort` -> `ModelProvider` bridge with deterministic fake-provider tests. It must preserve all existing runtime fail-closed behavior and must not introduce a real provider SDK in the same increment.
