# Controlled Analysis Tools

## Purpose

The controlled tool layer is the only future model-callable boundary over XuanMoney's deterministic finance-analysis services.

It exists to prevent a future LLM planner from gaining implicit access to Python execution, arbitrary files, SQL, dynamic imports, or financial write operations.

## Current model-callable tools

### `analyze_financials`

Accepts a typed `AnalyzeFinancialsRequest` containing normalized financial statements and returns a validated `FinanceAgentState` result.

It may compute:

- profitability metrics;
- period variance;
- exact net-profit Profit Bridge;
- configured deterministic validations and findings.

### `analyze_dimension`

Accepts a typed `AnalyzeDimensionRequest` containing normalized dimensional rows and returns a `DimensionalAnalysisResult`.

It may compute:

- one named business dimension at a time;
- member revenue and COGS aggregation;
- member gross profit and gross margin;
- period member contribution and exact dimension reconciliation.

## Explicitly excluded from the model-callable surface

The registry does not expose:

- `load_income_statements`;
- `load_dimensional_rows`;
- filesystem paths or arbitrary file reads;
- SQL or database connections;
- Python/shell/code execution;
- dynamic imports or dynamic tool registration;
- ERP/bank/tax integrations;
- payment, posting, filing, mutation, or deletion operations.

Ingestion remains an application-owned boundary until a separate file-access policy is designed and reviewed.

## Registry invariant

`AnalysisToolRegistry` contains a fixed code-reviewed set of `_ToolSpec` definitions. There is no public `register()` method.

Every registered model-callable tool must:

1. have a fixed unique name;
2. be classified `read_only`;
3. define a Pydantic request model;
4. define a Pydantic response model;
5. expose JSON Schema metadata from those models;
6. reject unknown tool names;
7. reject invalid request structures before execution;
8. normalize execution failures through `ToolInvocationError` / `ToolFailure`;
9. validate the handler response before returning it.

## Request policy

Tool request envelopes use `extra="forbid"`. Unknown top-level control parameters are rejected rather than silently ignored.

Request-validation errors use Pydantic error metadata with input values omitted. This prevents validation failures from unnecessarily echoing raw input values into future model/tool error messages.

## Error contract

Tool failures use one of these stable codes:

```text
unknown_tool
invalid_request
execution_failed
invalid_response
```

A failure carries:

```text
code
tool
message
details[]
```

The future model adapter should treat a tool failure as data about the attempted operation, not as permission to improvise an unregistered alternative.

For example, failure of `analyze_dimension` must not cause a planner to fall back to generated SQL or Python.

## Risk boundary

The current registry admits only `ToolRisk.READ_ONLY` tools. Adding a write-capable risk class is not part of this milestone and must not be done implicitly.

Financial write operations will require a separate governance milestone with authorization, approval, audit, idempotency, and transactional controls.

## Future LLM adapter rule

A future planner/synthesizer may:

- inspect tool metadata;
- select an existing registered tool;
- construct a request matching its schema;
- consume validated structured output;
- explain or summarize that output.

It may not:

- define new tools at runtime;
- change formulas or semantic mappings;
- bypass tool validation;
- call unregistered code paths;
- transform arithmetic contribution into causal claims without a separately validated causal method.
