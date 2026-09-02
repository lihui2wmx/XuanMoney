# Canonical Handoff

## Current status

Milestone: **Dimensional Analysis v0.1**

Status: **REVIEW CANDIDATE — PR #2 open as draft; inspect current-head checks before changing review/integration state**

Development branch: `feat/dimensional-analysis-v0.1`

Integration PR: `#2 — feat: add one-dimensional business variance analysis`

Base: `main` at `d65aeda6f0e22319768d0a8213f8c73fd7436eec`, which contains the squash-merged Finance Agent v0.1 core from PR #1.

The project is licensed under **Apache License 2.0**.

Latest fully verified branch HEAD before this handoff-only update: `8f7b8758df481c68fb51015f499e77826bd6f159`.

Both push-triggered and PR-triggered GitHub Actions checks completed successfully at that HEAD on the official GitHub-hosted `ubuntu-latest` runner. This handoff commit is documentation-only; inspect its current-head checks before marking PR #2 ready or making an integration decision.

## Implemented capabilities

The merged baseline already provides:

- deterministic income-statement profitability metrics and period variance;
- exact net-profit Profit Bridge reconciliation;
- balance-sheet identity validation;
- explicit CSV/XLSX income-statement semantic mapping and provenance;
- bounded read-only service/orchestration contracts;
- repository-native AI handoff workflow.

PR #2 adds:

- typed `DimensionalRow`, member metric, contribution, variance, and dimensional analysis result contracts using `Decimal`;
- explicit semantic mapping for `period`, `dimension`, `member`, `currency`, `revenue`, and `cogs`;
- CSV/XLSX dimensional ingestion with file/worksheet/row provenance;
- deterministic aggregation by one selected `(period, dimension, member)` level;
- member revenue, COGS, gross profit, and gross margin;
- zero-revenue gross margin represented as undefined;
- period comparison across the union of members, including new and disappearing members;
- exact member gross-profit contribution reconciliation to the selected dimension total;
- fail-closed mixed-currency aggregation/comparison without an FX policy;
- deterministic `analyze_dimension` service boundary without an LLM;
- tests covering aggregation, provenance, semantic mapping, CSV/XLSX, zero revenue, new/disappearing members, reconciliation, missing semantics, and currency mismatch.

## Dimensional contract

Canonical source fields:

```text
period
dimension
member
currency   # optional; defaults to CNY
revenue
cogs
```

The source must explicitly carry both `dimension` and `member`. A source column named `product`, `department`, `region`, or similar is **not** silently interpreted as the dimensional contract.

For a member:

```text
gross_profit = revenue - cogs
gross_margin = gross_profit / revenue
```

`gross_margin` is undefined when `revenue == 0`.

For period comparison:

```text
member_gross_profit_change = Δmember_revenue - Δmember_cogs
```

A member absent from one period is treated as zero in that period so new/disappearing members remain visible. The sum of member gross-profit changes must reconcile exactly to the selected dimension's total gross-profit change under `Decimal` arithmetic.

This is deterministic arithmetic contribution analysis, **not causal root-cause inference**.

## Trust boundary

The project remains read-only. Do not add or infer:

- payments or bank transfers;
- journal posting or ERP write-back;
- tax filing;
- deletion/update of financial records;
- unrestricted SQL;
- model-defined accounting formulas or metric semantics;
- model-guessed spreadsheet or business-dimension semantics;
- implicit multi-dimensional cube behavior;
- causal claims from arithmetic contribution alone;
- automatic FX conversion without an explicit policy;
- autonomous financial actions.

An LLM may be introduced later only above controlled deterministic tools and validators.

## Verification

Canonical local command:

```bash
python -m pip install -e ".[dev]"
pytest
```

CI policy:

- GitHub-hosted official runner labels only;
- current core runner: `ubuntu-latest`;
- no `self-hosted` runner;
- checkout/runtime setup uses GitHub-maintained actions.

Verified code/documentation anchor before this handoff update:

```text
8f7b8758df481c68fb51015f499e77826bd6f159
push CI: success
PR CI:   success
```

## Integration state

PR #2 targets `main` from `feat/dimensional-analysis-v0.1` and is the bounded integration unit for Dimensional Analysis v0.1.

A new AI agent should first inspect:

1. current PR #2 head SHA;
2. all current-head checks/CI;
3. review submissions and unresolved review threads;
4. whether the user requested review, integration, or further development.

If this handoff-only commit is green and there are no blocking review threads, PR #2 can be marked ready for review. Do **not** merge it implicitly without an explicit integration request or repository workflow decision.

Do not add the next tool-interface feature to PR #2.

## Known limitations

- the income-statement model remains intentionally simplified and is not complete PRC GAAP/IFRS coverage;
- no balance-sheet CSV/XLSX ingestion exists yet;
- no selling/admin/R&D automatic aggregation into operating expenses exists yet;
- dimensional analysis supports one explicitly named dimension at a time only;
- no multi-dimensional OLAP/cube query model exists;
- no FX conversion policy exists;
- dimensional contribution explains arithmetic member impact, not causal operational drivers;
- no controlled tool registry, LLM planner, database, API, or UI exists yet.

## Recommended next bounded action

**Complete review readiness for PR #2.**

If current-head CI is green, mark PR #2 ready for review and leave it as the integration boundary.

After PR #2 is reviewed and merged, create a fresh branch from updated `main` for **Controlled Analysis Tools v0.1**.

### Proposed future tool increment

Expose a small typed read-only registry over existing deterministic operations, for example:

```text
analyze_financials
analyze_dimension
load_income_statements
load_dimensional_rows
```

The tool layer should define explicit request/response schemas, tool names, allowed operations, validation behavior, and error contracts before any LLM planner is allowed to call it.

### Non-goals for the future tool increment

Do not add:

- financial write tools;
- unrestricted SQL;
- free-form Python execution;
- multi-dimensional cube behavior;
- causal inference;
- forecasting;
- autonomous LLM loops;
- UI or ERP integration.
