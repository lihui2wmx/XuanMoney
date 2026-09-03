# Canonical Handoff

## Current status

Milestone: **Provider Configuration & Safety Contract v0.1**

Status: **READY FOR INTEGRATION — implementation reviewed; final current-head CI required**

Development branch: `feat/provider-configuration-safety-v0.1`

Integration PR: **#10 — `feat: add provider configuration safety contract v0.1`**

Base: `main` at `23964aaafdf6d3e341550d6c01712e22ecb5b130`, which contains ModelPort Provider Bridge v0.1 and its post-merge handoff synchronization.

The project is licensed under **Apache License 2.0**.

## Implemented provider safety boundary

The branch defines provider-neutral configuration and transport-failure contracts before any real provider SDK or network call:

```text
application-owned configuration / future secret resolver
        |
        v
ProviderConfiguration + CredentialReference
        |
        v
future provider adapter
        |
        +--> ProviderTransportError / ProviderFailure
        |
        v
ModelProvider
        |
        v
ModelPortProviderBridge
        |
        v
BoundedModelRuntime
```

Implemented:

- immutable `ProviderConfiguration` with non-blank `provider_id` and `model_id`;
- integer `request_timeout_seconds` bounded to 1–120 seconds;
- `max_attempts` fixed to exactly `1` and protected against post-validation mutation;
- immutable optional `CredentialReference` carrying only a source and reference identifier, never a secret value;
- current credential-reference source limited to `environment` and environment-variable identifier syntax;
- unknown fields rejected with `extra="forbid"`, including attempted API-key/secret fields;
- stable `ProviderFailureCode` taxonomy;
- immutable `ProviderFailure` with `message` derived only from the stable failure code, preventing provider-supplied public diagnostics;
- `ProviderTransportError` exposing only the sanitized `ProviderFailure` contract;
- deterministic tests for configuration bounds, blank identifiers, retry expansion/mutation, secret-field rejection, stable failure mapping, failure immutability, and message/diagnostic injection rejection;
- `docs/PROVIDER_SAFETY.md` documenting the trust boundary.

## Preserved architecture

Existing path remains:

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge
        -> ModelProvider
        -> provider adapter (future)
```

No `src/xuanmoney/runtime/*`, Finance Kernel, Tool Registry, CI workflow, or dependency changes are part of PR #10.

Runtime invariant remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

## Explicitly out of scope

- OpenAI/Anthropic/Gemini or any other provider SDK;
- API-key values or secret persistence;
- environment-variable reading or secret resolution;
- external provider network calls;
- retry/backoff or provider fallback;
- streaming or provider-specific function calling;
- logging/metrics infrastructure;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write actions.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

Verified implementation anchor:

```text
6cefbdac58371bb80b06019aa22c2f67b5d93cb6
```

- PR CI #214: **success**;
- GitHub-hosted `ubuntu-latest`;
- Python 3.12;
- PR #10 non-draft and mergeable at integration review;
- no review submissions or unresolved review threads existed at review time;
- changed-file audit found only provider-model contracts/tests and governance documentation, with no runtime/finance/tool/CI/dependency expansion.

This handoff synchronization advances the branch beyond the verified implementation anchor, so the latest HEAD must also pass CI before merge.

## Integration review

No remaining architecture or safety blocker was found at implementation anchor `6cefbdac...`.

Review specifically confirmed:

- secret values have no declared serializable configuration field;
- environment credential references are reference names rather than resolved values;
- timeout and retry policy are bounded and immutable after validation;
- public failure text is code-derived rather than provider-supplied;
- public failure objects have no diagnostic/request/credential field;
- package dependency direction remains unchanged;
- no real SDK, network call, retry/fallback, new tool, or financial execution surface entered the branch.

## Recommended next bounded action

**If latest PR #10 current-head CI is green, squash-merge PR #10.**

After integration, refresh canonical handoff on a documentation-only branch before selecting any real provider SDK milestone.
