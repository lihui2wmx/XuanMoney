# Bounded Model Runtime

## Purpose

The bounded runtime is the provider-independent control plane between a future model adapter and XuanMoney's controlled read-only analysis tools.

Its purpose is not to create a generally autonomous agent. Its purpose is to permit a narrowly bounded model-assisted flow while keeping execution authority in deterministic, code-reviewed components.

## Hard execution sequence

A run may perform only this sequence:

```text
user query
   |
   v
PlanningRequest
   |
   v
ModelPort.plan()                # exactly once
   |
   v
validated PlannerDecision
   |                    \
   | tool_call           \ no_tool
   v                       v
AnalysisToolRegistry          terminate
.invoke()                      without synthesis
   |
   | exactly once at most
   v
validated structured tool result
   |
   v
SynthesisRequest
   |
   v
ModelPort.synthesize()          # exactly once
   |
   v
validated SynthesisOutput
   |
   v
RuntimeResult.complete
```

There is no internal retry loop, ReAct loop, recursive planning, automatic alternate-tool selection, or fallback execution path.

## Provider-independent model port

`ModelPort` defines only:

```text
plan(PlanningRequest) -> object
synthesize(SynthesisRequest) -> object
```

The return type is deliberately `object`. Provider adapters are not trusted to return valid structured data; runtime-owned Pydantic models validate all model output before it can influence execution or become a final answer.

No vendor SDK is part of this milestone.

## Planning contract

The planner receives:

```text
query
registered tool metadata[]
```

Tool metadata comes from `AnalysisToolRegistry` and contains the code-reviewed read-only tool names plus request/response JSON Schemas.

The planner can return exactly one of:

### Tool call

```json
{
  "kind": "tool_call",
  "tool": "analyze_financials",
  "arguments": {}
}
```

### No tool

```json
{
  "kind": "no_tool",
  "reason": "No registered deterministic tool can answer this request."
}
```

The structured plan uses `extra="forbid"` and whitespace stripping. Empty/whitespace-only tool names or reasons are invalid.

A tool name in model output has no authority by itself. It must resolve through `AnalysisToolRegistry`; unknown names fail closed.

## Tool execution contract

The runtime invokes at most one registered tool.

If the selected tool is unknown, its arguments fail request validation, or its deterministic execution fails, the run terminates with `RuntimeStatus.TOOL_FAILED`.

The runtime does **not** ask the planner to try again and does not substitute another tool.

In particular, tool failure never authorizes fallback to:

- Python or shell execution;
- SQL;
- filesystem reads;
- application-owned ingestion loaders;
- dynamic imports;
- external financial systems;
- financial write actions.

## Synthesis contract

Synthesis happens only after a successful validated tool result.

The synthesizer receives:

```text
original query
tool name
validated structured tool result
```

It does not receive an arbitrary execution environment.

The synthesizer is called exactly once. Its output must validate as:

```json
{"answer": "non-empty text"}
```

Whitespace-only answers are rejected. Synthesis failure terminates the run; it is not retried automatically.

## Failure contract

Runtime-level failures are classified as:

```text
planner_exception
invalid_plan
synthesis_exception
invalid_synthesis
```

Tool-level failures retain the controlled registry's typed tool failure codes.

Provider exception strings are intentionally not copied into public `RuntimeResult` messages. A future observability layer may record implementation diagnostics under a separate redaction and access policy, but provider exception text is not part of the model/user-facing runtime contract.

Pydantic validation errors omit raw input values from structured error details.

## Status contract

A run ends in exactly one status:

```text
complete
no_tool
planner_failed
tool_failed
synthesis_failed
```

There is no hidden continuation after one of these terminal states.

## Testing policy

The runtime is tested first with deterministic fake models.

Tests must verify at minimum:

- exactly one planning call in every run;
- at most one tool execution;
- synthesis only after successful tool execution;
- exactly one synthesis call when synthesis is reached;
- no synthesis after no-tool, planning failure, or tool failure;
- unknown tool names fail closed;
- invalid tool arguments fail closed;
- planner/synthesizer structured outputs are validated;
- whitespace-only structured strings are rejected where required;
- provider exceptions do not leak their raw messages into `RuntimeResult`;
- no automatic retry/fallback behavior is introduced.

Provider adapter tests come later and must not weaken these runtime invariants.

## Future provider adapter rule

A future provider adapter may translate between an external model API and `ModelPort`, but it must not:

- call XuanMoney tools directly;
- implement its own tool retry loop;
- bypass `AnalysisToolRegistry`;
- add hidden tools;
- execute model-generated code;
- alter financial formulas or semantic mappings;
- turn arithmetic contribution results into unsupported causal claims.

The runtime owns execution policy; the provider adapter owns only model I/O translation.
