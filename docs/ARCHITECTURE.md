# Architecture

## Goal

XuanMoney is a trustworthy finance-analysis agent. A model may choose among approved analysis tools and explain validated results, but financial facts, formulas, semantic mappings, validation, reconciliation, evidence, tool permissions, provider selection, credential handling, and execution policy remain deterministic and application-owned.

## Current data and model flow

```text
CSV / XLSX / normalized rows
        |
        v
Semantic Registry + Application-owned Ingestion
        |
        +------------------------------+
        |                              |
        v                              v
IncomeStatement                 DimensionalRow
        |                              |
        v                              v
Finance Kernel                  Dimensional Kernel
  - profitability metrics         - member aggregation
  - period variance               - gross profit/margin
  - profit bridge                 - period member contribution
        |                              |
        +---------------+--------------+
                        |
                        v
                    Validators
              - accounting identity
              - profit bridge tie-out
              - dimensional tie-out
                        |
                        v
                 Service Boundaries
            - analyze_financials
            - analyze_dimension
                        |
                        v
              Controlled Tool Registry
            - fixed read-only names
            - typed request schemas
            - typed response schemas
            - stable failure contract
                        ^
                        |
                BoundedModelRuntime
          plan -> <=1 tool -> synthesize
                        |
                        v
                     ModelPort
              - plan(PlanningRequest)
              - synthesize(SynthesisRequest)
                        |
                        v
              ModelPortProviderBridge
                        |
                        v
                   ModelProvider
              - complete(ModelRequest)
                        |
                        v
              ProviderFactoryRegistry
          # application-owned allowlist
                        |
                        v
               OpenAIProviderFactory
          # trusted credential reveal
                        |
                        v
               OpenAIProviderAdapter
          # timeout / max_retries=0
                        |
                        v
                OpenAI Responses API
```

The bounded runtime, provider transport contract, credential boundary, provider factory registry, and first real OpenAI provider adapter are integrated. Normal CI remains deterministic and does not use a live provider credential or network request.

## Module boundaries

### `domain.py`
Typed financial statements, dimensional rows, evidence, metrics, contribution results, and validation contracts. Monetary values use `Decimal`. Evidence can include `dimension` and `member` context when applicable.

### `semantic/`
Explicit semantic registries. Unknown or ambiguous external fields must never be promoted into canonical finance/business semantics by free-form model inference.

### `ingestion/`
Read-only CSV/XLSX adapters owned by the application boundary. They are **not** model-callable tools because no model filesystem-access policy exists.

### `finance/`
Deterministic domain layer with no LLM dependency. Current capabilities include profitability metrics, period variance, balance-sheet validation, net-profit bridge decomposition, and one-dimensional gross-profit contribution analysis.

### `agent/`
Bounded application orchestration state for deterministic finance analysis.

### `service.py`
Application boundaries for `analyze_financials` and `analyze_dimension`.

### `tools/`
The only model-callable execution boundary. `AnalysisToolRegistry` exposes a fixed code-reviewed set of read-only operations, JSON Schema metadata, typed request/response validation, and stable failure semantics. See `docs/TOOLS.md`.

### `runtime/`
Owns model-assisted execution policy and adapters that depend on runtime contracts. `BoundedModelRuntime` performs exactly one planning call, invokes at most one registered tool, and performs one synthesis call only after successful tool execution. `ModelPortProviderBridge` implements the runtime-facing `ModelPort` while adapting the lower-level provider transport. Runtime validates planner/synthesis outputs and normalizes failures. See `docs/RUNTIME.md`.

### `model/`
Owns the lower-level provider-neutral transport surface only: `ModelRequest`, `ModelResponse`, `ModelProvider`, provider configuration, credential references, and stable provider failures. This package remains independent of `xuanmoney.runtime`, credentials, providers, and financial/tool execution modules. See `docs/PROVIDER_CONTRACT.md` and `docs/PROVIDER_SAFETY.md`.

### `credentials/`
Application-owned credential-resolution boundary. Resolved secrets are wrapped by `ProtectedSecret`, are redacted/non-serializable, and may be revealed only at an explicitly trusted provider/client-construction boundary. The concrete environment resolver receives an injected mapping rather than exposing process environment access to lower layers. See `docs/CREDENTIALS.md`.

### `providers/`
Application-owned provider composition and provider-specific integration layer. It owns `ProviderAdapterComposer`, immutable `ProviderFactoryRegistry`, trusted provider factories, and real provider adapters. The first integrated adapter is OpenAI Responses API. Only this layer imports the OpenAI SDK. See `docs/PROVIDER_COMPOSITION.md`, `docs/PROVIDER_REGISTRY.md`, and `docs/OPENAI_PROVIDER_ADAPTER.md`.

Allowed dependency direction includes:

```text
providers   -> credentials -> model
providers   -> model
runtime     -> model
```

Forbidden reverse dependencies include:

```text
model       -X-> credentials
model       -X-> providers
credentials -X-> providers
model       -X-> runtime
```

A future application runtime-composition module may depend on providers, credentials, runtime, and tools to wire existing boundaries together; lower layers must not depend upward on that application composition module.

## Controlled tool invariant

The model-callable set is exactly:

```text
analyze_financials
analyze_dimension
```

The registry does not expose filesystem loaders, SQL, Python/shell execution, dynamic imports, provider configuration, credential resolution, provider selection, or write actions.

Every registered tool has a fixed name, read-only risk class, Pydantic request/response model, deterministic handler, and JSON Schema metadata. Unknown tools and invalid requests fail closed.

A tool execution failure never authorizes the model layer, runtime, bridge, or provider to improvise an alternate execution path.

## Runtime invariant

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

`BoundedModelRuntime` remains the owner of:

- validation of `PlannerDecision`;
- enforcement of the controlled registry;
- tool request/response validation through the registry;
- validation of `SynthesisOutput`;
- terminal failure classification;
- provider exception sanitization.

The bridge and provider do not weaken or duplicate these controls.

## Provider bridge invariant

The bridge may only translate model I/O:

```text
PlanningRequest
  -> ModelRequest(phase=planning, request, response_schema)
  -> ModelProvider.complete()
  -> strict JSON decode
  -> untrusted object
  -> runtime validation

SynthesisRequest
  -> ModelRequest(phase=synthesis, request, response_schema)
  -> ModelProvider.complete()
  -> strict JSON decode
  -> untrusted object
  -> runtime validation
```

Each reached model phase performs one provider call. Malformed JSON, non-standard `NaN`/`Infinity` constants, or provider exceptions terminate through the existing runtime exception boundary; the bridge does not retry.

## Provider selection, configuration, and credential invariant

Provider selection is application-owned and fail-closed:

```text
ProviderConfiguration.provider_id
        -> ProviderFactoryRegistry
        -> trusted ProviderAdapterFactory
```

There is no public runtime registration, dynamic import, entry-point/plugin discovery, filesystem discovery, model-controlled provider loading, or provider fallback.

Provider configuration is immutable and non-secret. `request_timeout_seconds` is bounded, `max_attempts` is fixed to `1`, and credential objects are references only. Secret resolution remains outside model/runtime/tool/finance surfaces.

`ProtectedSecret.reveal()` is permitted only at an explicitly trusted provider/client-construction boundary and never for diagnostics, prompts, evidence, logging, or serialization.

## OpenAI provider invariant

The integrated first provider uses the official OpenAI Python SDK and Responses API only:

```text
OpenAIProviderFactory
  -> OpenAI(api_key=<revealed>, timeout=<configured>, max_retries=0)
  -> OpenAIProviderAdapter
  -> one responses.create() per complete()
```

The existing transport contract is preserved:

```text
ModelRequest.prompt   -> Responses instructions
ModelRequest.context  -> deterministic JSON -> Responses input
```

The adapter does not enable provider-native tools, function calling, streaming, background responses, retries, fallback, or autonomous provider loops. Stable public provider failures contain code-derived safe messages only and do not retain raw provider diagnostics or credentials.

Normal CI uses deterministic fake SDK clients; live credentials and provider network calls are outside current acceptance tests.

## Income-statement Profit Bridge invariant

```text
net_profit = revenue
           - cogs
           - operating_expenses
           + other_income
           - other_expenses
           - taxes
```

Therefore:

```text
Δnet_profit = +Δrevenue
              -Δcogs
              -Δoperating_expenses
              +Δother_income
              -Δother_expenses
              -Δtaxes
```

The bridge reconciles exactly under `Decimal` arithmetic.

## Dimensional-analysis invariant

The dimensional schema remains deliberately narrow:

```text
period
dimension
member
currency
revenue
cogs
source
```

For one selected `(dimension, period)` slice:

```text
member_gross_profit = member_revenue - member_cogs
member_gross_margin = member_gross_profit / member_revenue
```

Gross margin is undefined when member revenue is zero.

For period comparison:

```text
member_gross_profit_change = Δmember_revenue - Δmember_cogs
```

New and disappearing members use zero for the absent period. The sum of member gross-profit changes must reconcile exactly to the selected dimension's total gross-profit change. Mixed currencies fail closed because no FX policy exists.

This is arithmetic contribution analysis, not causal inference.

## Provenance invariant

A material result remains traceable to available source data:

```text
file -> worksheet (XLSX) -> row -> canonical field
     -> period/dimension/member -> aggregate/contribution -> validated result
```

Transformations must not discard provenance silently.

## Trust boundaries

Free-form model reasoning, provider adapters, and the provider bridge never define or bypass:

- financial formulas;
- accounting identities or reconciliation rules;
- canonical metric semantics;
- business dimension/member semantics;
- source-of-truth values;
- unknown spreadsheet mappings;
- tool registration or risk classification;
- provider selection or provider registry mutation;
- credential resolution or secret reveal policy;
- permission checks;
- arbitrary filesystem, SQL, Python, or shell execution;
- financial write actions.

## CI boundary

Core CI uses GitHub-hosted runner labels only. Current Python CI runs on `ubuntu-latest` with GitHub-maintained `actions/checkout` and `actions/setup-python`. `self-hosted` runners are outside project policy.

Provider adapter acceptance tests remain deterministic and network-free. Live credentials must not be required by normal CI.

## Next architecture increments

1. add **Application Runtime Composition v0.1** to wire validated provider configuration, injected credential resolution, fixed provider registry, provider bridge, controlled tool registry, and bounded runtime through one explicit application-owned construction boundary;
2. define any live-provider smoke/operational policy separately before introducing live-network validation or provider observability;
3. richer validation and a more complete financial statement model;
4. API/UI after runtime construction and result contracts stabilize;
5. multi-dimensional analysis only as a separate explicitly validated milestone;
6. financial write capabilities only under a separate authorization/approval/audit milestone.
