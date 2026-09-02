# Canonical Handoff

## Current status

Milestone: **Finance Agent v0.1**

Status: **ACTIVE — deterministic analysis core verified; dimensional analysis is next**

Development branch: `feat/finance-agent-v0.1`

Verified code/test anchor: `4eb9e56e59ccba5527f549a6a46d8e4184e43931`

At that anchor, GitHub Actions completed successfully on the GitHub-hosted `ubuntu-latest` runner with the ingestion and Profit Bridge test suites present. Commits after the anchor are documentation/handoff synchronization unless repository history shows otherwise; a new agent must still inspect current HEAD and CI before changing code.

## Implemented capabilities

- typed income statement and balance sheet contracts using `Decimal`;
- profitability metrics: gross profit, gross margin, operating profit, net profit;
- period-over-period metric variance;
- deterministic Profit Bridge decomposition of net-profit change;
- exact Profit Bridge reconciliation validator;
- balance-sheet identity validation;
- evidence-backed findings and source provenance;
- bounded `FinanceAgentState` orchestration boundary;
- CSV and XLSX income-statement ingestion;
- explicit Chinese/English semantic alias registry for the normalized v0.1 schema;
- fail-closed behavior for missing required fields, duplicate headers, and ambiguous semantic mappings;
- repository-native AI handoff workflow and open-source contribution workflow;
- unit tests and GitHub Actions CI.

## Trust boundary

v0.1 remains strictly read-only. The following are out of scope:

- payments or bank transfers;
- journal posting or ERP write-back;
- tax filing;
- deletion/update of financial records;
- unrestricted SQL;
- model-defined accounting formulas or metric semantics;
- model-guessed spreadsheet semantics;
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

## Profit Bridge contract

For the simplified current model:

```text
Δnet_profit = +Δrevenue
              -Δcogs
              -Δoperating_expenses
              +Δother_income
              -Δother_expenses
              -Δtaxes
```

Positive contribution means the line item improved net profit relative to the comparison period. Negative contribution means it reduced net profit. The contribution sum must reconcile exactly to net-profit change under `Decimal` arithmetic.

This is deterministic accounting decomposition, not causal business root-cause inference.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

CI policy:

- GitHub-hosted official runner labels only;
- current core runner: `ubuntu-latest`;
- no `self-hosted` runner;
- checkout/runtime setup uses GitHub-maintained actions.

## Known limitations

- the normalized income statement is intentionally simplified and is not yet a complete PRC GAAP/IFRS income-statement model;
- the semantic registry does not infer arbitrary user columns;
- no balance-sheet Excel/CSV ingestion exists yet;
- no automatic component aggregation (for example selling/admin/R&D expense into operating expenses) exists yet;
- no dimensional business data (department/product/customer) exists yet;
- Profit Bridge explains arithmetic line-item contribution, not causal operational drivers;
- no LLM, API, database, or UI integration exists yet.

## Recommended next bounded increment

**Dimensional Analysis v0.1 — one dimension at a time.**

Add a narrow normalized business dataset that can explain revenue and gross-profit variance across one explicit dimension such as department, product, region, or customer. Keep the first implementation generic through a `dimension` + `member` contract rather than hard-coding one business taxonomy.

### Proposed minimum data contract

```text
period
dimension
member
revenue
cogs
source/provenance
```

### Exit conditions

- typed dimensional row/result contracts use `Decimal`;
- ingestion is explicit and fail-closed for required fields;
- aggregation by `(period, dimension, member)` is deterministic;
- member-level revenue, COGS, gross-profit, and gross-margin metrics are available;
- period-to-period contribution analysis reconciles member totals back to the selected dimension total;
- evidence/provenance survives aggregation;
- tests cover new/disappearing members, zero revenue, positive/negative changes, and exact total reconciliation;
- service/tool boundary can request one named dimension without an LLM;
- architecture, development log, and this handoff are updated.

### Non-goals for the next increment

Do not add:

- multi-dimensional OLAP/cube behavior;
- causal inference;
- forecasting;
- LLM planning;
- database access;
- UI;
- ERP integration;
- payments or any financial write action.
