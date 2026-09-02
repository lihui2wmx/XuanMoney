# Development Log

## 2026-09-02 — Project bootstrap

Status: **ACTIVE — Finance Agent v0.1**

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

Status: **ACTIVE — verification pending final CI**

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

### Current boundary

Still no LLM integration, database access, UI, ERP integration, or financial write action. Semantic mapping remains explicit and deterministic.

### Next recommended increment

Implement **Profit Bridge v0.1** over the normalized `IncomeStatement`: deterministic contribution decomposition of period-to-period net-profit change with exact reconciliation and evidence. See `docs/HANDOFF.md` for exit conditions and non-goals.
