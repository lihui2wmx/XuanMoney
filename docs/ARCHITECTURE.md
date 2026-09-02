# Architecture

## Goal

XuanMoney is a trustworthy finance-analysis agent. The agent may eventually decide what analysis to perform, but financial facts, formulas, semantic mappings, validation, and evidence are produced by deterministic components.

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
        |
        v
Validator
  - accounting identities
        |
        v
Evidence-backed findings
        |
        v
Structured AnalysisResult
```

## Module boundaries

### `domain.py`
Typed financial statements and result contracts. Monetary values use `Decimal`. Statement models carry source provenance that is propagated into evidence.

### `semantic/`
Explicit finance semantic registry. It maps recognized external column names to canonical fields. It must fail closed on ambiguous mappings and must never use free-form LLM inference to define financial semantics.

### `ingestion/`
Read-only adapters that parse external tabular formats into canonical domain models. Format-specific behavior belongs here; financial formulas do not.

### `finance/`
Deterministic domain layer. It must not depend on an LLM or agent framework.

### `agent/`
Bounded orchestration state. Future model adapters belong above the finance layer and consume structured tool results.

### `service.py`
Application boundary that composes deterministic analysis workflows.

## Trust boundaries

The following are never delegated to free-form model reasoning:

- financial formulas;
- accounting identities;
- canonical metric semantics;
- source-of-truth values;
- spreadsheet column mappings not present in the semantic registry;
- permission checks;
- future financial write actions.

A future LLM layer may perform intent classification, planning, drill-down selection, natural-language explanation, and synthesis over validated structured results.

## Provenance invariant

A material metric or finding should remain traceable to the available source. For tabular ingestion the current provenance granularity is:

```text
file -> worksheet (XLSX only) -> row -> canonical field -> metric/finding
```

Future transformations must not discard provenance silently.

## CI boundary

Core CI uses GitHub-hosted runner labels only. Current Python CI runs on `ubuntu-latest` using GitHub-maintained `actions/checkout` and `actions/setup-python`. `self-hosted` runners are outside project policy.

## Next architecture increments

1. deterministic profit-bridge decomposition with exact reconciliation;
2. richer validation and a more complete financial statement model;
3. dimensional business data for department/product/customer drill-down;
4. controlled analysis tool interface;
5. LLM planner/synthesizer behind an explicit adapter;
6. API/UI only after the analysis contracts stabilize.
