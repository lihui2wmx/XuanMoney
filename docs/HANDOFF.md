# Canonical Handoff

## Current status

Milestone: **Provider Configuration & Safety Contract v0.1**

Status: **IMPLEMENTATION COMPLETE — current-head CI and integration review pending**

Development branch: `feat/provider-configuration-safety-v0.1`

Base: latest `main` after ModelPort Provider Bridge v0.1 and its post-merge documentation synchronization.

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

- `ProviderConfiguration` with non-blank `provider_id` and `model_id`;
- integer `request_timeout_seconds` bounded to 1–120 seconds;
- `max_attempts` fixed by type and validation to exactly `1`;
- optional `CredentialReference` that carries only a credential source and identifier, never a secret value;
- current credential-reference source limited to `environment`;
- unknown fields rejected with `extra="forbid"`, including attempted API-key/secret fields;
- stable `ProviderFailureCode` taxonomy;
- `ProviderFailure.message` derived only from the stable failure code, so adapters cannot inject raw public diagnostic text;
- `ProviderTransportError` exposing only the sanitized `ProviderFailure` contract;
- deterministic tests for configuration bounds, blank identifiers, retry expansion, secret-field rejection, stable failure mapping, and message/diagnostic injection rejection;
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

This milestone does not change `BoundedModelRuntime`, `ModelPortProviderBridge`, Finance Kernel, Tool Registry, or the runtime execution sequence.

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

CI policy:

- GitHub-hosted official runners only;
- `ubuntu-latest`;
- Python 3.12;
- no `self-hosted` runner.

Current branch changes require current-head CI verification before integration review or merge.

## Recommended next bounded action

**Verify current-head CI, then perform integration review for Provider Configuration & Safety Contract v0.1.**

Review should confirm that secret values have no serializable contract field, timeout/retry policy remains bounded, failure messages cannot carry provider-supplied diagnostic text, package dependency direction remains unchanged, and no SDK/network/execution-surface expansion entered the branch.
