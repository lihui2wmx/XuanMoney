# Architecture

## Goal

XuanMoney is a trustworthy finance-analysis agent. The agent may decide what analysis to perform, but financial facts, formulas, validation, and evidence are produced by deterministic components.

## v0.1 data flow

```text
Normalized financial data
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
Typed financial statements and result contracts. Monetary values use `Decimal`.

### `finance/`
Deterministic domain layer. It must not depend on an LLM or agent framework.

### `agent/`
Bounded orchestration state. Future model adapters belong above the finance layer and consume structured tool results.

### `service.py`
Current application boundary that composes the deterministic analysis workflow.

## Trust boundaries

The following are never delegated to free-form model reasoning:

- financial formulas;
- accounting identities;
- source-of-truth values;
- permission checks;
- future financial write actions.

A future LLM layer may perform intent classification, planning, drill-down selection, natural-language explanation, and synthesis over validated structured results.

## Next architecture increments

1. normalized Excel/CSV ingestion adapter;
2. semantic metric registry;
3. richer validation and profitability decomposition;
4. controlled analysis tool interface;
5. LLM planner/synthesizer behind an explicit adapter;
6. API/UI only after the analysis contracts stabilize.
