# Development Log

## 2026-09-02 — Project bootstrap

Status: **COMPLETE**

Established an empty-repository baseline and created `feat/finance-agent-v0.1`.

Implemented the first bounded analysis slice:

- typed income statement and balance sheet contracts using `Decimal`;
- evidence-bearing metric and finding models;
- gross profit, gross margin, operating profit, and net profit calculations;
- period-over-period metric variance;
- balance-sheet accounting identity validation;
- bounded agent state and read-only analysis workflow;
- unit tests for core calculations, validation, and decline findings.

### Boundary after bootstrap

No LLM integration, database access, Excel ingestion, UI, ERP integration, or financial write action was part of the bootstrap increment.

## 2026-09-02 — Normalized tabular ingestion and AI handoff workflow

Status: **COMPLETE**

Implemented the next bounded data-access slice:

- explicit Chinese/English semantic aliases for the v0.1 income-statement schema;
- fail-closed handling for required fields, duplicate columns, and ambiguous aliases;
- deterministic CSV ingestion;
- deterministic XLSX ingestion through `openpyxl`;
- `Decimal` parsing including comma-separated and accounting-negative values;
- source provenance from file/worksheet/row into `IncomeStatement` and downstream evidence;
- ingestion tests covering semantic mapping, ambiguity, CSV, XLSX, and missing required fields.

Integrated a repository-native development workflow so work can be resumed without chat history:

- expanded root `AGENTS.md` with mandatory AI startup and handoff rules;
- added `docs/AI_WORKFLOW.md` as the execution/verification protocol;
- added `docs/HANDOFF.md` as the canonical current-state checkpoint;
- added `CONTRIBUTING.md` for open-source contributors;
- added a finance/trust-aware pull request template;
- documented GitHub-hosted runner policy;
- hardened core CI with read-only permissions and a timeout.

The ingestion/workflow slice was exercised successfully by GitHub Actions on the official GitHub-hosted `ubuntu-latest` runner before the next code increment began.

## 2026-09-02 — Profit Bridge v0.1

Status: **ACTIVE — final branch CI verification pending**

Implemented deterministic net-profit change decomposition for the simplified v0.1 income statement:

- signed contributions for revenue, COGS, operating expenses, other income, other expenses, and taxes;
- exact `Decimal` reconciliation to period-over-period net-profit change;
- explicit reconciliation result and validator;
- provenance for both comparison periods on every bridge contribution;
- service-level integration into `AnalysisResult`;
- tests for contribution signs, cost/expense decreases, provenance, tamper detection, and service integration.

### Current boundary

Still no LLM integration, database access, UI, ERP integration, or financial write action. Profit attribution is limited to deterministic line-item bridge decomposition; it does not yet claim causal business root-cause analysis.

### Next recommended increment

Add **Dimensional Analysis v0.1** for a narrow business dataset with `period`, `dimension`, `member`, `revenue`, and `cogs`, then support deterministic drill-down of revenue/gross-profit variance by one dimension at a time. Do not add an LLM yet. See `docs/HANDOFF.md` for the canonical boundary after final verification.
