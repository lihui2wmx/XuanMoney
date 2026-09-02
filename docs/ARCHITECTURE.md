# Architecture

## Goal

XuanMoney is a trustworthy finance-analysis agent. A model may choose among approved analysis tools and explain validated results, but financial facts, formulas, semantic mappings, validation, reconciliation, evidence, tool permissions, and execution policy remain deterministic.

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
               Provider Adapter
                        |
                        v
          External model service (future)
```

No external provider SDK or network integration is implemented in the current bridge milestone.

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
Owns model-assisted execution policy. `BoundedModelRuntime` performs exactly one planning call, invokes at most one registered tool, and performs one synthesis call only after successful tool execution. It validates planner and synthesis outputs and normalizes failures. See `docs/RUNTIME.md`.

### `model/`
Owns provider-neutral model transport contracts and adapters. `ModelProvider.complete()` is lower-level than the runtime-facing `ModelPort`. `ModelPortProviderBridge` translates typed runtime requests into provider transport requests and JSON-decodes provider response content, but it does not own planner/synthesis semantic validation, tool execution, retries, or financial rules. See `docs/PROVIDER_CONTRACT.md`.

## Controlled tool invariant

The model-callable set is exactly:

```text
analyze_financials
analyze_dimension
```

The registry does not expose filesystem loaders, SQL, Python/shell execution, dynamic imports, or write actions.

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

The bridge does not weaken or duplicate these controls.

## Provider bridge invariant

The bridge may only translate model I/O:

```text
PlanningRequest
  -> ModelRequest(phase=planning, request, response_schema)
  -> ModelProvider.complete()
  -> JSON decode
  -> untrusted object
  -> runtime validation

SynthesisRequest
  -> ModelRequest(phase=synthesis, request, response_schema)
  -> ModelProvider.complete()
  -> JSON decode
  -> untrusted object
  -> runtime validation
```

Each reached model phase performs one provider call. Malformed JSON or provider exceptions terminate through the existing runtime exception boundary; the bridge does not retry.

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
- permission checks;
- arbitrary filesystem, SQL, Python, or shell execution;
- financial write actions.

## CI boundary

Core CI uses GitHub-hosted runner labels only. Current Python CI runs on `ubuntu-latest` with GitHub-maintained `actions/checkout` and `actions/setup-python`. `self-hosted` runners are outside project policy.

## Next architecture increments

1. integrate and review `ModelPort Provider Bridge v0.1` using deterministic fake providers only;
2. add a first real provider adapter only as a separate milestone after the bridge is integrated and re-verified;
3. define provider configuration/credential and observability policy before production network use;
4. richer validation and a more complete financial statement model;
5. API/UI after runtime and result contracts stabilize;
6. multi-dimensional analysis only as a separate explicitly validated milestone;
7. financial write capabilities only under a separate authorization/approval/audit milestone.
