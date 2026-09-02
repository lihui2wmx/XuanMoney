# Bounded Model Runtime

## Purpose

The bounded runtime is the provider-independent control plane between model I/O and XuanMoney's controlled read-only analysis tools.

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

The return type is deliberately `object`. Provider-facing code is not trusted to return valid structured data; runtime-owned Pydantic models validate all model output before it can influence execution or become a final answer.

## ModelPort provider bridge

`ModelPortProviderBridge` implements `ModelPort` over the lower-level provider-neutral `ModelProvider.complete(ModelRequest) -> ModelResponse` contract.

For each reached phase the bridge:

1. receives the typed runtime request;
2. serializes it into a provider-neutral `ModelRequest` context with an explicit `planning` or `synthesis` phase;
3. includes the expected response JSON Schema as provider guidance;
4. performs exactly one `ModelProvider.complete()` call;
5. JSON-decodes `ModelResponse.content`;
6. returns the decoded object to `BoundedModelRuntime` for the existing runtime-owned validation.

The bridge does not validate `PlannerDecision` or `SynthesisOutput`, execute tools, retry providers, or select alternate execution paths.

Malformed provider JSON or a provider exception propagates out of the bridge and is normalized by the existing runtime phase boundary. Valid JSON with an invalid planner/synthesis shape is rejected by the existing runtime validation path.

No vendor SDK or network provider is part of the bridge milestone.

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

The provider bridge preserves this distinction:

- provider exception or malformed transport JSON -> planner/synthesis exception;
- decoded but structurally invalid planner/synthesis object -> invalid plan/synthesis;
- no bridge-level retry in either case.

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

The runtime and bridge are tested with deterministic fakes before any real provider integration.

Tests must verify at minimum:

- exactly one planning call in every run;
- at most one tool execution;
- synthesis only after successful tool execution;
- exactly one synthesis call when synthesis is reached;
- no synthesis after no-tool, planning failure, or tool failure;
- unknown tool names fail closed;
- invalid tool arguments fail closed;
- planner/synthesizer structured outputs are validated by the runtime;
- whitespace-only structured strings are rejected where required;
- provider exceptions do not leak their raw messages into `RuntimeResult`;
- no automatic retry/fallback behavior is introduced;
- the bridge makes exactly one provider call for each reached phase;
- a complete runtime run works through a deterministic fake provider;
- malformed provider JSON and provider exceptions terminate without bridge-level retry.

## Provider adapter rule

A future real provider adapter may sit below `ModelPortProviderBridge`, but it must not:

- call XuanMoney tools directly;
- implement its own autonomous tool retry loop;
- bypass `AnalysisToolRegistry` or `BoundedModelRuntime`;
- add hidden tools;
- execute model-generated code;
- alter financial formulas or semantic mappings;
- turn arithmetic contribution results into unsupported causal claims.

Provider-specific credentials, network policy, observability/redaction, timeouts, and SDK behavior require a separate milestone and review.

The runtime owns execution policy; the bridge and provider adapter own only model I/O translation.
