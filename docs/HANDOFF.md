# Canonical Handoff

## Current status

Milestone: **Model Provider Contract v0.1**

Status: **READY FOR INTEGRATION — integration-review blockers resolved; merge requires current-head CI green**

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
- typed provider transport contract tests;
- explicit tests that the provider contract does not expose the runtime `ModelPort` or financial execution surface;
- provider boundary documentation and synchronized repository handoff state.

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

Verified anchors:

- `795f9a9c84040242bfb8ee562ebf90b1c75c6664`: contract-test corrections, PR CI #114 success;
- `30d1aae10187d715b055a63a246b67a4a6385723`: architecture/test-semantics corrections, PR CI #126 success.

This final handoff/development-state synchronization follows those verified anchors. Merge only if the latest branch HEAD also has successful CI.

## Integration review

The first review found three blockers:

1. documentation/tests implied direct `BoundedModelRuntime -> ModelProvider` integration although the runtime actually depends on `ModelPort`;
2. `AGENTS.md`, `docs/DEVELOPMENT_LOG.md`, and this handoff disagreed on the active milestone and PR #5 state;
3. the handoff lacked a concrete base SHA and still described pre-PR actions.

All three were corrected. The second review confirmed:

- no `src/xuanmoney/runtime/*` change;
- no Finance Kernel or Tool Registry change;
- no external provider SDK/network path;
- no filesystem/SQL/Python/shell execution expansion;
- no financial write expansion;
- feature branch is ahead of, and not behind, `main`;
- PR #6 remains mergeable.

No remaining integration blocker is known other than the standard current-head CI gate.

## Recommended next bounded action

**If current-head PR #6 CI is green, squash-merge PR #6.**

After integration, start a fresh branch for a bounded `ModelPort` -> `ModelProvider` bridge. Do not connect a real provider SDK until that bridge is implemented and tested against the existing fail-closed runtime behavior.
