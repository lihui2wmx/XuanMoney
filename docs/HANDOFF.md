# Canonical Handoff

## Current status

Milestone: **Controlled Analysis Tools v0.1**

Status: **READY FOR INTEGRATION REVIEW — PR #4 open; inspect current-head checks and review state before merge**

Development branch: `feat/controlled-analysis-tools-v0.1`

Integration PR: `#4 — feat: add controlled read-only analysis tool registry`

Base: `main` at `6e7334c3fbd576c7f6657ca8f5b70a6a0ceb193c`, which contains Dimensional Analysis v0.1 merged through PR #3.

The project is licensed under **Apache License 2.0**.

Latest fully verified branch HEAD before this handoff-only update: `fbaa346952ea86edea329025718cb1b9f960884c`.

The push-triggered GitHub Actions test completed successfully at that HEAD on the official GitHub-hosted `ubuntu-latest` runner. Opening PR #4 and this handoff-only commit trigger fresh checks; inspect current-head checks before integration.

## Implemented capabilities

The merged baseline provides:

- deterministic profitability metrics and period variance;
- exact net-profit Profit Bridge reconciliation;
- balance-sheet identity validation;
- explicit CSV/XLSX financial ingestion and provenance;
- one-dimensional member aggregation and exact gross-profit contribution reconciliation;
- bounded deterministic `analyze_financials` and `analyze_dimension` service boundaries;
- repository-native AI handoff and Apache-2.0 open-source workflow.

PR #4 adds the future model-callable boundary:

- `AnalysisToolRegistry` with a fixed code-reviewed tool set;
- no public runtime `register()` API;
- model-callable names limited to `analyze_financials` and `analyze_dimension`;
- `ToolRisk.READ_ONLY` enforced for registered operations;
- typed Pydantic request/response contracts;
- JSON Schema metadata for future model adapters;
- top-level request envelopes with `extra="forbid"`;
- stable failure codes: `unknown_tool`, `invalid_request`, `execution_failed`, `invalid_response`;
- validation details with raw input values omitted;
- normalization of service/domain failures through `ToolInvocationError` / `ToolFailure`;
- response validation before tool results are returned;
- tests for successful invocation, schema metadata, unknown tools, extra parameters, filesystem-tool exclusion, request errors, and execution failures;
- `docs/TOOLS.md` defining the tool trust boundary.

## Model-callable contract

Current model-callable set:

```text
analyze_financials
analyze_dimension
```

Explicitly **not** model-callable:

```text
load_income_statements
load_dimensional_rows
filesystem paths
SQL/database access
Python/shell execution
dynamic imports
dynamic tool registration
ERP/bank/tax integrations
financial write operations
```

Application-owned ingestion remains outside the model-callable registry until a separate file-access policy is designed and reviewed.

Tool failure does not authorize fallback to an unregistered capability.

## Trust boundary

The project remains read-only. Do not add or infer:

- payment or bank-transfer execution;
- journal posting or ERP write-back;
- tax filing;
- deletion/update of financial records;
- unrestricted SQL;
- arbitrary Python/shell execution;
- model-defined formulas, metric semantics, spreadsheet semantics, or business dimensions;
- runtime tool creation/import;
- implicit multi-dimensional cube behavior;
- causal claims from arithmetic contribution alone;
- automatic FX conversion without an explicit policy;
- open-ended autonomous agent loops.

No external LLM/provider is integrated in PR #4.

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

Verified anchor before this handoff update:

```text
fbaa346952ea86edea329025718cb1b9f960884c
push CI: success
```

## Integration state

PR #4 targets `main` from `feat/controlled-analysis-tools-v0.1` and is the bounded integration unit for Controlled Analysis Tools v0.1.

A new AI agent should inspect:

1. current PR #4 head SHA;
2. all current-head push/PR checks;
3. review submissions and unresolved review threads;
4. whether the requested action is review, integration, or further development.

If current-head checks are green and there are no blocking review threads, PR #4 is ready for squash integration under the existing bounded workflow.

Do not add model-runtime/provider code to PR #4.

## Known limitations

- the financial statement model remains intentionally simplified and is not complete PRC GAAP/IFRS coverage;
- balance-sheet CSV/XLSX ingestion is not implemented;
- no automatic selling/admin/R&D aggregation into operating expenses exists;
- dimensional analysis supports one explicitly named dimension at a time;
- no FX conversion policy exists;
- contribution analysis is arithmetic, not causal inference;
- filesystem ingestion is application-owned, not model-callable;
- no provider-independent model runtime exists yet;
- no external LLM provider, database, API, or UI integration exists yet.

## Recommended next bounded action

**Integrate PR #4 after current-head verification.**

After PR #4 is merged, create a fresh branch from updated `main` for **Bounded Model Runtime v0.1**.

### Proposed future runtime increment

Implement a provider-independent model port and a single-step planner/synthesizer runtime tested with deterministic fake models.

The runtime should permit only this bounded sequence:

```text
user query
  -> planner sees registered tool metadata
  -> planner selects at most one registered tool + schema-valid arguments
  -> registry executes/validates tool
  -> synthesizer receives query + validated tool result
  -> final answer
```

The runtime must enforce the tool name against the registry rather than trusting arbitrary model output.

### Exit conditions for the future runtime increment

- provider-independent planner/synthesizer protocol exists with no vendor SDK dependency;
- planner output is typed and permits at most one tool call;
- selected tool must exist in `AnalysisToolRegistry`;
- tool arguments pass the existing request schema before execution;
- tool failure terminates the bounded run rather than triggering an autonomous fallback loop;
- synthesizer receives only the original query plus structured validated result/failure data needed for explanation;
- deterministic fake-model tests cover valid selection, unknown tool, invalid arguments, tool execution failure, and final synthesis;
- no open-ended ReAct loop or arbitrary retry behavior exists;
- architecture, development log, and canonical handoff are updated.

### Non-goals for the future runtime increment

Do not add:

- an external LLM/provider SDK;
- multi-step autonomous tool loops;
- arbitrary filesystem access;
- financial write tools;
- unrestricted SQL/Python execution;
- multi-dimensional cubes;
- causal inference;
- forecasting;
- UI or ERP integration.
