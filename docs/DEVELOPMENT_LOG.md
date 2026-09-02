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

Added:

- explicit Chinese/English semantic aliases;
- fail-closed required/duplicate/ambiguous field handling;
- CSV/XLSX ingestion using `openpyxl`;
- deterministic decimal parsing;
- file/worksheet/row provenance;
- repository-native AI handoff (`AGENTS.md`, `docs/AI_WORKFLOW.md`, `docs/HANDOFF.md`);
- open-source contribution guidance and PR template;
- GitHub-hosted runner policy and hardened CI.

## 2026-09-02 — Profit Bridge v0.1

Status: **COMPLETE — merged via PR #1**

Added deterministic net-profit change decomposition:

- signed revenue/COGS/expense/other-income/tax contributions;
- exact `Decimal` reconciliation to net-profit change;
- bridge validation and provenance;
- service-level integration and tests.

PR #1 also established Apache License 2.0 licensing. The v0.1 deterministic core was squash-merged to `main` at `d65aeda6f0e22319768d0a8213f8c73fd7436eec` after successful GitHub-hosted CI.

## 2026-09-02 — Dimensional Analysis v0.1

Status: **ACTIVE — implementation complete, final PR verification pending**

Branch: `feat/dimensional-analysis-v0.1`

Implemented the next bounded read-only slice:

- typed `DimensionalRow`, member metrics, contribution, variance, and analysis result contracts;
- explicit semantic mapping for `period`, `dimension`, `member`, `currency`, `revenue`, and `cogs`;
- CSV/XLSX dimensional ingestion with source provenance;
- deterministic aggregation by one `(period, dimension, member)` hierarchy level;
- member revenue, COGS, gross profit, and gross margin;
- zero-revenue gross margin represented as undefined;
- period comparison across the union of members, including new/disappearing members;
- exact member gross-profit contribution reconciliation to dimension total;
- fail-closed mixed-currency comparison without an FX policy;
- deterministic `analyze_dimension` service boundary without an LLM;
- tests for aggregation, provenance, semantic mapping, CSV/XLSX, zero revenue, new/disappearing members, reconciliation, missing semantics, and currency mismatch.

The code-and-test slice passed GitHub Actions on the official GitHub-hosted `ubuntu-latest` runner at `1b5b359577d5d52212cda614f7ee2106accbffe9`; an additional XLSX provenance test and documentation updates followed and require final branch/PR verification.

### Boundary

This milestone remains single-dimensional and read-only. It does not implement multi-dimensional OLAP, causal inference, forecasting, LLM planning, database access, UI, ERP integration, or financial write actions.

### Next recommended increment after integration

Add a **controlled typed analysis-tool interface** that exposes the existing deterministic finance and dimensional kernels as a small registry of read-only operations. Do not add free-form LLM orchestration until that tool boundary is explicit and tested.
