# Canonical Handoff

## Current status

Milestone: **Model Provider Contract v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `c8f18f93b72cd0f4462e0f94a2cbbaebcdafa305`

Merged PR: **#6 — `feat: establish model provider contract v0.1`**

The project is licensed under **Apache License 2.0**.

## Integrated provider boundary

The repository now contains a provider-neutral lower-level model transport contract beneath the existing runtime-facing `ModelPort`:

```text
BoundedModelRuntime
        -> ModelPort
        -> future bounded ModelPort/provider bridge
        -> ModelProvider
        -> Provider Adapter
        -> external model service (future)
```

`BoundedModelRuntime` still depends on `ModelPort.plan()` and `ModelPort.synthesize()`. No `ModelPort` -> `ModelProvider` bridge exists yet.

Integrated through PR #6:

- typed `ModelRequest` / `ModelResponse` schemas with `extra="forbid"`;
- provider-neutral `ModelProvider.complete(ModelRequest) -> ModelResponse` protocol;
- `BaseModelAdapter` implementation boundary;
- deterministic `EchoModelAdapter` for tests only;
- provider transport contract tests;
- explicit separation between provider transport and runtime orchestration;
- `docs/PROVIDER_CONTRACT.md`.

## Runtime invariant

The runtime policy remains unchanged:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

Future provider work must not:

- bypass `BoundedModelRuntime` or `ModelPort` execution policy;
- call financial tools directly;
- invoke unrestricted SQL, Python, shell, filesystem, or dynamic imports;
- add hidden tools or hidden retries;
- alter financial formulas, semantic mappings, validators, or permissions;
- perform financial write operations;
- introduce an autonomous ReAct loop.

## Verification

PR #6 final head:

```text
6e204f11fee6a887580b9b4b06d2538831c6bbe8
```

Verification:

- GitHub Actions PR CI #130: **success**;
- runner: GitHub-hosted `ubuntu-latest`;
- Python 3.12;
- PR was non-draft and mergeable at integration;
- squash merge commit: `c8f18f93b72cd0f4462e0f94a2cbbaebcdafa305`.

## Known limitations

- no real external model provider exists;
- no provider credentials/configuration exists;
- no provider network call exists;
- no streaming or function-calling provider implementation exists;
- no `ModelPort` -> `ModelProvider` bridge exists;
- application filesystem ingestion remains outside the model-callable surface;
- no unrestricted SQL/Python execution exists;
- no financial write tools exist.

## Recommended next bounded action

**Start `ModelPort Provider Bridge v0.1` on a fresh feature branch.**

The bridge should:

1. implement the existing runtime-facing `ModelPort.plan()` and `ModelPort.synthesize()` interface over an injected `ModelProvider`;
2. translate only typed planning/synthesis requests to provider transport requests;
3. convert provider responses back into values that the existing runtime already validates;
4. preserve provider exception sanitization and all fail-closed runtime behavior;
5. use deterministic fake providers for tests;
6. introduce no external provider SDK, credentials, network calls, hidden retries, new tools, or financial write paths.

Do not combine the bridge with a real OpenAI/Anthropic/Gemini adapter. That must remain a later, separate milestone.
