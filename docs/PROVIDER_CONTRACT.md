# Model Provider Contract v0.1

## Scope

This document defines a provider-neutral transport contract for future external model integrations.

The contract introduced in this milestone does **not** replace the existing runtime-facing `ModelPort`, and it is not yet wired directly into `BoundedModelRuntime`.

## Architecture boundary

The current intended layering is:

```text
BoundedModelRuntime
        |
        v
ModelPort
  - plan(PlanningRequest)
  - synthesize(SynthesisRequest)
        |
        v
future ModelPort/provider bridge
        |
        v
ModelProvider
  - complete(ModelRequest)
        |
        v
Provider Adapter
        |
        v
External model service
```

`BoundedModelRuntime` continues to own orchestration policy and depends only on `ModelPort`.

`ModelProvider` is a lower-level provider transport boundary. A future bounded bridge may translate typed runtime planning/synthesis requests into `ModelRequest` values and validate provider responses back into the existing runtime contracts. That bridge is intentionally out of scope for v0.1.

## Contract

`ModelProvider.complete()` accepts a typed `ModelRequest` and returns a typed `ModelResponse`.

The provider layer may:

- translate a provider-neutral model request into provider-specific request payloads;
- translate provider responses into `ModelResponse`;
- expose provider metadata through the response contract.

The provider layer must not own runtime planning, tool selection, tool execution, financial semantics, validation policy, or autonomous control flow.

## Forbidden responsibilities

Provider implementations and adapters must not:

- bypass `BoundedModelRuntime` or `ModelPort` execution policy;
- invoke financial tools directly;
- access unrestricted SQL, Python, shell, filesystem, or dynamic imports;
- modify financial formulas, semantic mappings, validators, or permissions;
- create hidden model-callable tools;
- implement autonomous retry or ReAct loops;
- perform financial write operations.

## Current implementation

This milestone contains:

- `ModelRequest` / `ModelResponse` with `extra="forbid"`;
- a provider-neutral `ModelProvider` protocol;
- `BaseModelAdapter` as the provider implementation boundary;
- deterministic `EchoModelAdapter` coverage for contract tests;
- no vendor SDK, credentials, network call, streaming, function-calling implementation, or provider-specific behavior.

The current tests verify the provider transport contract only. They do not claim that `BoundedModelRuntime` is already wired to `ModelProvider`.

## Next architectural boundary

After this contract is integrated, any real provider milestone must first define and test a bounded adapter from the existing `ModelPort.plan()` / `ModelPort.synthesize()` interface to this lower-level provider contract. It must preserve the runtime invariant:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```
