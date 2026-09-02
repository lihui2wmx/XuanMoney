# Canonical Handoff

## Current status

Milestone: **Bounded Model Runtime v0.1**

Status: **IMPLEMENTATION COMPLETE — final current-head CI verification pending; no integration PR open**

Development branch: `feat/bounded-model-runtime-v0.1`

Base: `main` at `9934248ade818b66ff14f385ee8063f0791ce837`, which contains Controlled Analysis Tools v0.1 merged through PR #4.

The project is licensed under **Apache License 2.0**.

## Implemented runtime boundary

The branch adds a provider-independent model runtime above the existing controlled tool registry:

```text
user query
  -> ModelPort.plan() exactly once
  -> typed PlannerDecision
  -> at most one AnalysisToolRegistry invocation
  -> validated structured tool result
  -> ModelPort.synthesize() exactly once
  -> validated final answer
```

The runtime has no autonomous retry loop and no ReAct-style continuation.

Implemented contracts and behavior include:

- provider-independent `ModelPort`; no vendor SDK dependency;
- typed planning and synthesis requests/responses with `extra="forbid"`;
- planner decision restricted to `no_tool` or one `tool_call`;
- tool name enforced by `AnalysisToolRegistry` rather than trusted from model output;
- tool arguments validated through the existing tool request schema;
- unknown tool, invalid arguments, and tool execution failure terminate the run;
- synthesis occurs only after a successful tool result;
- planner and synthesis provider exceptions normalize to stable failures without embedding provider exception text;
- whitespace-only planner reasons and synthesis answers fail validation;
- deterministic fake-model tests cover complete, no-tool, unknown-tool, invalid-argument, tool-failure, invalid-plan, planner-exception, invalid-synthesis, and synthesis-exception paths;
- `docs/RUNTIME.md` defines the provider/runtime trust boundary.

## Runtime invariant

Current runtime policy is:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

A model/provider adapter must not:

- create or register hidden tools;
- invoke SQL, Python, shell, filesystem, or dynamic imports outside the registry;
- retry a failed tool autonomously;
- fall back to an unregistered execution path;
- alter financial formulas, semantic mappings, validators, or permissions;
- perform financial write actions;
- introduce a multi-step autonomous agent loop.

Provider adapters translate model I/O only. Execution policy remains owned by `BoundedModelRuntime` and `AnalysisToolRegistry`.

## Model-callable tools

Current allowed set remains:

```text
analyze_financials
analyze_dimension
```

Application-owned ingestion remains outside the model-callable surface.

## Verification

Canonical local command:

```bash
python -m pip install -e ".[dev]"
pytest
```

CI policy:

- GitHub-hosted official runners only;
- current runner: `ubuntu-latest`;
- no `self-hosted` runner;
- GitHub-maintained checkout/runtime setup actions.

Verified runtime code/test anchor:

```text
e8ac6c6d06d2b33a8dd7fe8627f1b80301940f7c
push CI: success
```

A documentation-only `docs/RUNTIME.md` update and the current milestone/handoff synchronization followed that verified anchor. Inspect the latest branch HEAD and its checks before opening an integration PR.

## Integration state

There is currently **no PR** for Bounded Model Runtime v0.1.

Do not merge or start provider integration until the current branch HEAD has successful CI.

## Known limitations

- no external LLM/provider adapter exists;
- no provider authentication/configuration exists;
- no API/UI exists;
- the financial statement model remains intentionally simplified;
- dimensional analysis remains one dimension at a time;
- no FX conversion policy exists;
- application filesystem ingestion is not model-callable;
- no unrestricted SQL/Python execution exists;
- no financial write tools exist.

## Recommended next bounded action

**Verify current-head CI only.**

If the current branch HEAD is green, the next separate bounded action is to open a non-draft integration PR for **Bounded Model Runtime v0.1**. Do not implement an external model provider in that same PR.
