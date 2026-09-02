# Canonical Handoff

## Current status

Milestone: **Finance Agent v0.1**

Status: **ACTIVE**

Development branch: `feat/finance-agent-v0.1`

The repository has a deterministic, read-only finance-analysis core plus the first normalized tabular-ingestion and semantic-mapping layer. The current branch is not yet an integration candidate until the new ingestion slice is verified by CI and the handoff is refreshed with the verified HEAD.

## Implemented capabilities

- typed income statement and balance sheet contracts using `Decimal`;
- profitability metrics: gross profit, gross margin, operating profit, net profit;
- period-over-period metric variance;
- balance-sheet identity validation;
- evidence-backed findings and source provenance;
- bounded `FinanceAgentState` orchestration boundary;
- CSV and XLSX income-statement ingestion;
- explicit Chinese/English semantic alias registry for the normalized v0.1 schema;
- fail-closed behavior for missing required fields, duplicate headers, and ambiguous semantic mappings;
- unit tests and GitHub Actions CI.

## Trust boundary

v0.1 remains strictly read-only. The following are out of scope:

- payments or bank transfers;
- journal posting or ERP write-back;
- tax filing;
- deletion/update of financial records;
- unrestricted SQL;
- model-defined accounting formulas or metric semantics;
- autonomous financial actions.

An LLM may be introduced later only above deterministic tools and validators.

## Current ingestion contract

The normalized income-statement schema currently recognizes:

- `period`;
- `currency`;
- `revenue`;
- `cogs`;
- `operating_expenses`;
- `other_income`;
- `other_expenses`;
- `taxes`.

Only explicit aliases in `src/xuanmoney/semantic/registry.py` are accepted. Unknown columns are ignored rather than inferred. Required semantic fields are `period`, `revenue`, and `cogs`.

## Verification state

The earlier finance-kernel slice passed GitHub Actions. The ingestion slice added in the current development session still requires a final CI check after all documentation/workflow changes are committed.

Local verification command:

```bash
python -m pip install -e ".[dev]"
pytest
```

CI policy: GitHub-hosted official runner labels only; current core runner is `ubuntu-latest`. No `self-hosted` runner.

## Known limitations

- the normalized income statement is intentionally simplified and is not yet a complete PRC GAAP/IFRS income-statement model;
- the semantic registry does not infer arbitrary user columns;
- no balance-sheet Excel/CSV ingestion exists yet;
- no automatic component aggregation (for example selling/admin/R&D expense into operating expenses) exists yet;
- no dimensional business data (department/product/customer) exists yet;
- no profit-bridge/root-cause decomposition exists yet;
- no LLM, API, database, or UI integration exists yet.

## Recommended next bounded increment

**Profit Bridge v0.1 over normalized income statements.**

Implement deterministic period-to-period net-profit contribution decomposition across the fields already present in `IncomeStatement`, with reconciliation back to total net-profit change and evidence for each contribution.

### Exit conditions

- each supported line-item contribution has an explicit sign convention and formula;
- the sum of contributions exactly reconciles to the computed net-profit variance within `Decimal` arithmetic;
- a reconciliation validator fails closed when the bridge does not tie;
- tests cover revenue increase/decrease, cost increase/decrease, expense/tax changes, and exact reconciliation;
- service-level analysis can emit a structured profit-bridge result without an LLM;
- architecture, development log, and this handoff are updated.

### Non-goals for the next increment

Do not add LLM orchestration, dimensional drill-down, database access, UI, ERP integration, payments, or financial write actions in the profit-bridge increment.
