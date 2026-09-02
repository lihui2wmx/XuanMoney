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

Status: **COMPLETE — merged via PR #3**

Implemented:

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

Draft PR #2 was closed unmerged only because the connected GitHub GraphQL action failed when changing draft status. The same branch and code boundary were re-opened as non-draft PR #3. Final push/PR checks passed on GitHub-hosted `ubuntu-latest`, and PR #3 was squash-merged to `main` at `6e7334c3fbd576c7f6657ca8f5b70a6a0ceb193c`.

### Boundary

This milestone remains single-dimensional and read-only. It does not implement multi-dimensional OLAP, causal inference, forecasting, LLM planning, database access, UI, ERP integration, or financial write actions.

## 2026-09-02 — Controlled Analysis Tools v0.1

Status: **ACTIVE — implementation complete, documentation/PR verification pending**

Branch: `feat/controlled-analysis-tools-v0.1`

Implemented a fixed future model-callable boundary over the deterministic services:

- `AnalysisToolRegistry` with no public dynamic `register()` API;
- model-callable tools limited to `analyze_financials` and `analyze_dimension`;
- `ToolRisk.READ_ONLY` classification enforced at registry construction;
- Pydantic request and response models with exported JSON Schema metadata;
- `extra="forbid"` on tool request envelopes;
- fixed failure codes: `unknown_tool`, `invalid_request`, `execution_failed`, `invalid_response`;
- validation errors omit raw input values from structured error details;
- service/domain failures normalized through `ToolInvocationError` / `ToolFailure`;
- response-model validation before tool results are returned;
- application file loaders, SQL, Python/shell execution, dynamic imports, and financial write operations excluded from the model-callable registry;
- tests for registry contents, metadata, successful finance/dimensional invocation, unknown tools, filesystem-tool exclusion, request validation, extra parameters, and execution failures;
- `docs/TOOLS.md` defining the model/tool trust boundary.

The initial implementation and subsequent tightened request/failure contract both passed core tests on the official GitHub-hosted `ubuntu-latest` runner before final documentation updates.

### Current boundary

No external LLM/provider SDK is part of this milestone. The registry is the deterministic contract that any future planner must use.

### Next recommended increment after integration

Add a **provider-independent bounded model port and single-step planner/synthesizer runtime**. Test it first with deterministic fake models. Do not connect an external LLM provider until the runtime proves it cannot bypass the controlled registry or enter an open-ended autonomous loop.
