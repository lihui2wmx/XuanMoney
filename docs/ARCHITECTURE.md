# Architecture

## Goal

XuanMoney is a trustworthy finance-analysis agent. A future model may decide which approved analysis to request and how to explain the validated result, but financial facts, formulas, semantic mappings, validation, reconciliation, evidence, and tool permissions remain deterministic.

## Current data flow

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
                        |
                        v
              Future bounded model port
                        |
                        v
              Future planner/synthesizer
```

## Module boundaries

### `domain.py`
Typed financial statements, dimensional rows, evidence, metrics, contribution results, and validation contracts. Monetary values use `Decimal`. Evidence can include `dimension` and `member` context when applicable.

### `semantic/`
Explicit semantic registries. Unknown or ambiguous external fields must never be promoted into canonical finance/business semantics by free-form model inference.

### `ingestion/`
Read-only CSV/XLSX adapters owned by the application boundary. They are **not** currently model-callable tools because no model filesystem-access policy exists.

### `finance/`
Deterministic domain layer with no LLM dependency. Current capabilities include profitability metrics, period variance, balance-sheet validation, net-profit bridge decomposition, and one-dimensional gross-profit contribution analysis.

### `agent/`
Bounded orchestration state for finance analysis. Future model/runtime components belong above the controlled tool registry and must not bypass it.

### `service.py`
Application boundaries for `analyze_financials` and `analyze_dimension`.

### `tools/`
The only intended future model-callable boundary. `AnalysisToolRegistry` exposes a fixed code-reviewed set of read-only operations, JSON Schema metadata, typed request/response validation, and stable failure semantics. See `docs/TOOLS.md`.

## Controlled tool invariant

The initial model-callable set is exactly:

```text
analyze_financials
analyze_dimension
```

The registry does not expose filesystem loaders, SQL, Python/shell execution, dynamic imports, or write actions.

Every registered tool must have:

```text
fixed name
read_only risk class
Pydantic request model
Pydantic response model
handler
JSON Schema metadata
```

Unknown tools and invalid request envelopes fail closed. Top-level extra request fields are forbidden. Handler outputs are validated before being returned.

A tool execution failure is represented through `ToolInvocationError` carrying a typed `ToolFailure` with one of:

```text
unknown_tool
invalid_request
execution_failed
invalid_response
```

A future model must not treat a tool failure as permission to improvise an unregistered execution path.

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

Free-form model reasoning never defines or bypasses:

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

A future LLM layer may inspect approved tool metadata, choose a registered tool, provide schema-valid arguments, and synthesize explanations over validated structured results.

## CI boundary

Core CI uses GitHub-hosted runner labels only. Current Python CI runs on `ubuntu-latest` with GitHub-maintained `actions/checkout` and `actions/setup-python`. `self-hosted` runners are outside project policy.

## Next architecture increments

1. bounded provider-independent model port and single-step planner/synthesizer runtime over the controlled registry;
2. provider adapter(s) only after the model port and runtime are tested with deterministic fakes;
3. richer validation and a more complete financial statement model;
4. API/UI after runtime and result contracts stabilize;
5. multi-dimensional analysis only as a separate explicitly validated milestone;
6. financial write capabilities only under a separate authorization/approval/audit milestone.
