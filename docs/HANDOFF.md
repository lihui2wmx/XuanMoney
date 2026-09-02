# Canonical Handoff

## Current status

Milestone: **Model Provider Contract v0.1**

Status: **READY FOR SECOND INTEGRATION REVIEW — architectural/documentation corrections applied; current-head CI verification pending**

Development branch: `feat/model-provider-contract-v0.1`

Integration PR: **#6 — `feat: establish model provider contract v0.1`**

Base: `main` at `d3fb61a789e70f2e4029605462a294543e6fdc39`, which contains Bounded Model Runtime v0.1 merged through PR #5.

The project is licensed under **Apache License 2.0**.

## Implemented provider boundary

The branch adds a provider-neutral lower-level model transport contract beneath the existing runtime-facing `ModelPort`:

```text
BoundedModelRuntime
        -> ModelPort
        -> future bounded ModelPort/provider bridge
        -> ModelProvider
        -> Provider Adapter
        -> external model service (future)
```

The bridge between `ModelPort` and `ModelProvider` is **not implemented in this milestone**. `BoundedModelRuntime` still depends on `ModelPort.plan()` and `ModelPort.synthesize()` exactly as merged in PR #5.

Implemented in PR #6:

- typed `ModelRequest` / `ModelResponse` schemas with `extra="forbid"`;
- provider-neutral `ModelProvider.complete(ModelRequest) -> ModelResponse` protocol;
- `BaseModelAdapter` implementation boundary;
- deterministic `EchoModelAdapter` for tests only;
- typed provider contract tests;
- provider boundary documentation.

## Runtime invariant

The merged runtime policy remains unchanged:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

Provider contracts and future provider adapters must not:

- bypass `BoundedModelRuntime` or `ModelPort` execution policy;
- call financial tools directly;
- invoke unrestricted SQL, Python, shell, filesystem, or dynamic imports;
- add hidden tools or hidden retries;
- alter financial formulas, semantic mappings, validators, or permissions;
- perform financial write operations;
- introduce an autonomous ReAct loop.

## Scope exclusions

This milestone contains no:

- external model SDK;
- API key or provider credential handling;
- external model network call;
- streaming;
- function-calling implementation;
- provider-specific behavior;
- `ModelPort` -> `ModelProvider` bridge;
- Finance Kernel or Tool Registry change;
- financial write path.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

CI policy:

- GitHub-hosted official runners only;
- current runner: `ubuntu-latest`;
- no `self-hosted` runner.

The contract-test correction anchor `795f9a9c84040242bfb8ee562ebf90b1c75c6664` passed PR CI. Subsequent integration-review corrections synchronize the provider architecture and repository handoff state, so inspect the latest branch HEAD and its checks before merge.

## Review state

The first integration review found two blocking inconsistencies:

1. documentation and tests implied that `BoundedModelRuntime` was already integrated directly with `ModelProvider`, although the runtime actually depends on `ModelPort`;
2. `AGENTS.md`, `docs/DEVELOPMENT_LOG.md`, and this handoff did not agree on the active milestone and PR #5 integration state.

Those inconsistencies have been corrected on the feature branch. No runtime execution policy or financial behavior was changed by the correction.

## Recommended next bounded action

**Verify current-head PR #6 CI, then perform the second integration review.**

If current-head CI is green and the second review finds no remaining blocker, PR #6 is eligible for integration. Do not add a real model provider or the `ModelPort`/provider bridge to PR #6.
