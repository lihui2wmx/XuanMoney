# Model Provider Contract v0.1

## Scope

This document defines the provider-neutral transport contract for future external model integrations and the bounded bridge from the runtime-facing `ModelPort` to that transport contract.

The provider contract does not own runtime execution policy. `BoundedModelRuntime` continues to depend on `ModelPort`, and `ModelPortProviderBridge` is the only adapter between that runtime-facing interface and `ModelProvider` in the current architecture.

## Architecture boundary

```text
BoundedModelRuntime
        |
        v
ModelPort
  - plan(PlanningRequest)
  - synthesize(SynthesisRequest)
        |
        v
ModelPortProviderBridge
        |
        v
ModelProvider
  - complete(ModelRequest)
        |
        v
Provider Adapter
        |
        v
External model service (future)
```

There is still no external provider SDK or network integration.

## Provider transport contract

`ModelProvider.complete()` accepts a typed `ModelRequest` and returns a typed `ModelResponse`.

The provider layer may:

- translate a provider-neutral request into provider-specific request payloads;
- translate provider responses into `ModelResponse`;
- expose provider metadata through the response contract.

The provider layer must not own runtime planning, tool selection, tool execution, financial semantics, validation policy, retry policy, or autonomous control flow.

## ModelPort bridge contract

`ModelPortProviderBridge` implements the existing runtime-facing methods:

```text
plan(PlanningRequest) -> object
synthesize(SynthesisRequest) -> object
```

For planning, the bridge creates exactly one `ModelRequest` containing:

```text
phase = planning
request = serialized PlanningRequest
response_schema = PlannerDecision JSON Schema
```

For synthesis, the bridge creates exactly one `ModelRequest` containing:

```text
phase = synthesis
request = serialized SynthesisRequest
response_schema = SynthesisOutput JSON Schema
```

The bridge calls `ModelProvider.complete()` exactly once for each reached phase and JSON-decodes `ModelResponse.content`.

The decoded value remains untrusted. The bridge deliberately does **not** validate it as `PlannerDecision` or `SynthesisOutput`; `BoundedModelRuntime` remains the owner of those validation decisions.

## Failure boundary

The bridge contains no retry, fallback, alternate provider selection, or tool invocation.

If provider invocation raises or response content is not valid JSON, the exception propagates to the existing runtime phase boundary. `BoundedModelRuntime` then normalizes it to the existing terminal planner/synthesis exception result without echoing raw provider exception text.

If provider content is valid JSON but does not satisfy the planner/synthesis structured contract, the existing runtime validation produces `invalid_plan` or `invalid_synthesis` as before.

## Forbidden responsibilities

Provider implementations, provider adapters, and the bridge must not:

- bypass `BoundedModelRuntime` execution policy;
- invoke financial tools directly;
- access unrestricted SQL, Python, shell, filesystem, or dynamic imports;
- modify financial formulas, semantic mappings, validators, or permissions;
- create hidden model-callable tools;
- implement autonomous retry or ReAct loops;
- select alternate tools or execution paths after failure;
- perform financial write operations.

## Current implementation

The repository contains:

- `ModelRequest` / `ModelResponse` with `extra="forbid"`;
- provider-neutral `ModelProvider`;
- `BaseModelAdapter` as the provider implementation boundary;
- deterministic `EchoModelAdapter` contract coverage;
- `ModelPortProviderBridge`;
- deterministic fake-provider bridge tests including a real `BoundedModelRuntime` integration path.

No vendor SDK, credentials, network call, streaming, function-calling provider implementation, or provider-specific behavior is part of this milestone.

## Preserved runtime invariant

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

The bridge changes model I/O plumbing only; it does not expand the execution surface.
