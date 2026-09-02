# Architecture

## Goal

XuanMoney is a trustworthy finance-analysis agent. The agent may eventually decide what analysis to perform, but financial facts, formulas, semantic mappings, validation, reconciliation, and evidence are produced by deterministic components.

## v0.1 data flow

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
  - normalized statements
  - source provenance
        |
        v
FinanceAgentState
        |
        v
Finance Kernel
  - profitability metrics
  - period variance
  - profit bridge
        |
        v
Validator
  - accounting identities
  - bridge reconciliation
        |
        v
Evidence-backed findings/results
        |
        v
Structured AnalysisResult
```

## Module boundaries

### `domain.py`
Typed financial statements and result contracts. Monetary values use `Decimal`. Statement models carry source provenance that is propagated into evidence. Profit-bridge results expose both signed contributions and reconciliation difference.

### `semantic/`
Explicit finance semantic registry. It maps recognized external column names to canonical fields. It must fail closed on ambiguous mappings and must never use free-form LLM inference to define financial semantics.

### `ingestion/`
Read-only adapters that parse external tabular formats into canonical domain models. Format-specific behavior belongs here; financial formulas do not.

### `finance/`
Deterministic domain layer. It must not depend on an LLM or agent framework. Current capabilities include profitability metrics, period variance, balance-sheet validation, and net-profit bridge decomposition.

### `agent/`
Bounded orchestration state. Future model adapters belong above the finance layer and consume structured tool results.

### `service.py`
Application boundary that composes deterministic analysis workflows. When a prior period exists, it emits both metric variance and a reconciled profit bridge before deriving findings.

## Profit bridge invariant

For the simplified v0.1 income statement:

```text
net_profit = revenue
           - cogs
           - operating_expenses
           + other_income
           - other_expenses
           - taxes
```

Therefore period change must reconcile exactly as:

```text
Δnet_profit = +Δrevenue
              -Δcogs
              -Δoperating_expenses
              +Δother_income
              -Δother_expenses
              -Δtaxes
```

A positive contribution improves net profit relative to the comparison period. A negative contribution reduces it. Because the current formula is linear and all values use `Decimal`, the bridge validator requires exact reconciliation rather than a floating-point tolerance.

## Trust boundaries

The following are never delegated to free-form model reasoning:

- financial formulas;
- accounting identities and reconciliation rules;
- canonical metric semantics;
- source-of-truth values;
- spreadsheet column mappings not present in the semantic registry;
- permission checks;
- future financial write actions.

A future LLM layer may perform intent classification, planning, drill-down selection, natural-language explanation, and synthesis over validated structured results.

## Provenance invariant

A material metric or finding should remain traceable to the available source. For tabular ingestion the current provenance granularity is:

```text
file -> worksheet (XLSX only) -> row -> canonical field -> metric/bridge/finding
```

Future transformations must not discard provenance silently.

## CI boundary

Core CI uses GitHub-hosted runner labels only. Current Python CI runs on `ubuntu-latest` using GitHub-maintained `actions/checkout` and `actions/setup-python`. `self-hosted` runners are outside project policy.

## Next architecture increments

1. dimensional business data for department/product/customer drill-down;
2. richer validation and a more complete financial statement model;
3. controlled analysis tool interface;
4. LLM planner/synthesizer behind an explicit adapter;
5. API/UI only after the analysis contracts stabilize.
