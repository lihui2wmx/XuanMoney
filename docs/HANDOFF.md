# Canonical Handoff

## Current status

Milestone: **Provider Configuration & Safety Contract v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `0148962739a80cdb53c25dbbf445dc9584a75a4a`

Merged PR: **#10 — `feat: add provider configuration safety contract v0.1`**

The project is licensed under **Apache License 2.0**.

## Integrated provider safety boundary

The repository now defines provider-neutral configuration and transport-failure contracts before any real provider SDK or network call:

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

Integrated through PR #10:

- immutable `ProviderConfiguration` with non-blank `provider_id` and `model_id`;
- integer `request_timeout_seconds` bounded to 1–120 seconds;
- `max_attempts` fixed to exactly `1` and protected against post-validation mutation;
- immutable `CredentialReference` carrying only a credential source and reference identifier, never a secret value;
- current credential-reference source limited to `environment`, with environment-variable reference-name syntax;
- `extra="forbid"` rejection of unknown and attempted secret/API-key fields;
- stable `ProviderFailureCode` taxonomy;
- immutable `ProviderFailure` whose public `message` is derived only from the stable code;
- `ProviderTransportError` exposing only the sanitized public failure contract;
- deterministic tests covering configuration bounds, retry immutability, secret-field rejection, credential-reference syntax, stable failure mapping, failure immutability, and diagnostic/message injection rejection;
- `docs/PROVIDER_SAFETY.md` documenting the pre-SDK trust boundary.

## Preserved architecture

The integrated provider-neutral path remains:

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge
        -> ModelProvider
        -> provider adapter (future)
```

The runtime invariant remains unchanged:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

Provider Configuration & Safety v0.1 changed no runtime execution code, Finance Kernel, Tool Registry, CI workflow, dependency set, or model-callable surface.

## Verification

Final PR #10 head:

```text
93f2d2b8202cb55db31e82efbad11d61f9d78d4c
```

Verification:

- final PR CI #218: **success**;
- GitHub-hosted `ubuntu-latest` runner;
- Python 3.12;
- PR was non-draft and mergeable at final review;
- no unresolved review threads;
- final integration review ID `5096591938` found no remaining architecture or safety blocker;
- squash merge commit: `0148962739a80cdb53c25dbbf445dc9584a75a4a`.

## Current limitations

There is still no real external provider integration. Specifically:

- no credential resolver exists;
- no credential value is read from environment variables or a secret manager;
- no protected application-owned secret wrapper exists yet;
- no OpenAI/Anthropic/Gemini or other provider SDK;
- no external provider network call;
- no provider retry/backoff or fallback;
- no streaming or provider-specific function calling;
- no provider logging/metrics infrastructure;
- no production API/UI;
- no new model-callable tool or financial write capability.

## Recommended next bounded action

**Start `Credential Resolver Boundary v0.1` on a fresh feature branch.**

The bounded increment should:

1. define an application-owned `CredentialResolver` protocol that accepts the existing `CredentialReference`;
2. return a protected/opaque secret wrapper whose `repr`, string conversion, and serialization do not reveal the underlying credential;
3. keep resolved secret values out of `ProviderConfiguration`, `ModelRequest`, runtime results, evidence payloads, logs, and model-callable surfaces;
4. define deterministic sanitized resolver failure behavior for missing/unavailable references without echoing reference values or secret material;
5. use deterministic fake/in-memory resolver tests first;
6. preserve `max_attempts = 1`, the existing runtime invariant, and current package dependency direction.

Do **not** combine Credential Resolver Boundary v0.1 with a real OpenAI/Anthropic/Gemini SDK, actual provider network calls, streaming, retry/backoff, fallback, new analysis tools, or financial write behavior.
