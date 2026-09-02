# Architecture

## Goal

XuanMoney is a trustworthy finance-analysis agent. The agent may eventually decide what analysis to perform, but financial facts, formulas, semantic mappings, validation, reconciliation, and evidence are produced by deterministic components.

## Current data flow

```text
CSV / XLSX / normalized rows
        |
        v
Semantic Registry
  - explicit aliases
  - required-field checks
  - ambiguity rejection
        |
        v
Tabular Ingestion Adapter
  - Decimal parsing
  - source provenance
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
              Evidence-backed results
                        |
                        v
            Future controlled tool layer
                        |
                        v
              Future LLM planner/synthesizer
```

## Module boundaries

### `domain.py`
Typed financial statements, dimensional rows, evidence, metrics, contribution results, and validation contracts. Monetary values use `Decimal`. Evidence can include `dimension` and `member` context when applicable.

### `semantic/`
Explicit semantic registries. Unknown or ambiguous external fields must never be promoted into canonical finance/business semantics by free-form model inference.

### `ingestion/`
Read-only CSV/XLSX adapters. Current canonical contracts include both normalized income statements and one-dimensional business rows.

### `finance/`
Deterministic domain layer with no LLM dependency. Current capabilities include profitability metrics, period variance, balance-sheet validation, net-profit bridge decomposition, and one-dimensional gross-profit contribution analysis.

### `agent/`
Bounded orchestration state for the finance-analysis workflow. Future model adapters belong above deterministic finance tools.

### `service.py`
Application boundaries for `analyze_financials` and `analyze_dimension`. The dimensional service accepts one explicitly named dimension and does not perform autonomous drill-down.

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

The v0.1 dimensional schema is deliberately narrow:

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

New and disappearing members use zero for the absent period. The sum of member gross-profit changes must reconcile exactly to the selected dimension's total gross-profit change.

The kernel fails closed on mixed currencies because no FX conversion policy exists yet.

This is arithmetic contribution analysis, not causal inference.

## Provenance invariant

A material result remains traceable to available source data:

```text
file -> worksheet (XLSX) -> row -> canonical field
     -> period/dimension/member -> aggregate/contribution -> result
```

Transformations must not discard provenance silently.

## Trust boundaries

Free-form model reasoning never defines:

- financial formulas;
- accounting identities or reconciliation rules;
- canonical metric semantics;
- business dimension/member semantics;
- source-of-truth values;
- unknown spreadsheet mappings;
- permission checks;
- financial write actions.

A future LLM layer may select from controlled tools, choose an allowed drill-down path, and synthesize explanations over validated results.

## CI boundary

Core CI uses GitHub-hosted runner labels only. Current Python CI runs on `ubuntu-latest` with GitHub-maintained `actions/checkout` and `actions/setup-python`. `self-hosted` runners are outside project policy.

## Next architecture increments

1. controlled typed analysis-tool interface over the deterministic finance and dimensional kernels;
2. richer validation and a more complete financial statement model;
3. bounded LLM planner/synthesizer that can invoke only registered read-only tools;
4. API/UI after tool and result contracts stabilize;
5. multi-dimensional analysis only as a separate explicitly validated milestone.
