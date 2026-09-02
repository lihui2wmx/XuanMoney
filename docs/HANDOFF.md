# Canonical Handoff

## Current status

Milestone: **Finance Agent v0.1**

Status: **READY FOR REVIEW — PR #1 open; do not merge implicitly**

Development branch: `feat/finance-agent-v0.1`

Integration PR: `#1 — feat: establish Finance Agent v0.1 deterministic core`

Latest fully verified branch HEAD before this handoff-only update: `fe16fe996a3d5f216d860087a4d637bb400f6f01`

GitHub Actions completed successfully at that HEAD on the GitHub-hosted `ubuntu-latest` runner. PR #1 is open and mergeable. This handoff update is documentation-only; a new agent must inspect current PR checks before any integration decision.

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

## Integration state

PR #1 targets `main` from `feat/finance-agent-v0.1`. It is the bounded integration unit for the current v0.1 core.

A new AI agent should **not** merge PR #1 merely because it is mergeable. First inspect:

1. current PR head SHA;
2. current PR checks/CI;
3. unresolved review comments, if any;
4. whether the requested action is review, integration, or further development.

Do not add the next dimensional-analysis feature to PR #1. Keep this PR bounded.

## Known limitations

- the normalized income statement is intentionally simplified and is not yet a complete PRC GAAP/IFRS income-statement model;
- the semantic registry does not infer arbitrary user columns;
- no balance-sheet Excel/CSV ingestion exists yet;
- no automatic component aggregation (for example selling/admin/R&D expense into operating expenses) exists yet;
- no dimensional business data (department/product/customer) exists yet;
- Profit Bridge explains arithmetic line-item contribution, not causal operational drivers;
- no LLM, API, database, or UI integration exists yet;
- repository licensing has not been selected in this branch; do not choose a license silently on behalf of maintainers.

## Recommended next bounded action

**Review/integrate PR #1 when explicitly requested.**

After PR #1 is merged, create a fresh branch from updated `main` for **Dimensional Analysis v0.1 — one dimension at a time**.

### Proposed next implementation contract

```text
period
dimension
member
revenue
cogs
source/provenance
```

### Exit conditions for that future increment

- typed dimensional row/result contracts use `Decimal`;
- ingestion is explicit and fail-closed for required fields;
- aggregation by `(period, dimension, member)` is deterministic;
- member-level revenue, COGS, gross-profit, and gross-margin metrics are available;
- period-to-period contribution analysis reconciles member totals back to the selected dimension total;
- evidence/provenance survives aggregation;
- tests cover new/disappearing members, zero revenue, positive/negative changes, and exact total reconciliation;
- service/tool boundary can request one named dimension without an LLM;
- architecture, development log, and this handoff are updated.

### Non-goals for the future dimensional increment

Do not add:

- multi-dimensional OLAP/cube behavior;
- causal inference;
- forecasting;
- LLM planning;
- database access;
- UI;
- ERP integration;
- payments or any financial write action.
