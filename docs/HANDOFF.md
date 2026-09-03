# Canonical Handoff

## Current status

Milestone: **Credential Resolver Boundary v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `84edd3e90c9c5c2551e5314410bd7eb554cfe75e`

Merged PR: **#12 — `feat: add credential resolver boundary v0.1`**

The project is licensed under **Apache License 2.0**.

## Integrated credential boundary

The repository now contains an application-owned boundary between serializable credential references and future real provider integration:

```text
ProviderConfiguration
        |
        +--> CredentialReference            # serializable, non-secret
                  |
                  v
        CredentialResolver                  # xuanmoney.credentials
                  |
                  v
        ProtectedSecret                     # runtime-only, redacted/non-serializable
                  |
                  v
        future provider integration
```

Integrated through PR #12:

- `CredentialResolver.resolve(CredentialReference) -> ProtectedSecret` protocol;
- immutable `ProtectedSecret` rejecting empty values;
- redacted `str`, `repr`, and formatted output;
- JSON and pickle serialization fail closed;
- explicit `reveal()` reserved for a future trusted provider integration boundary;
- stable sanitized credential-resolution failure codes/messages;
- missing-reference fake resolution avoids retaining a secret-bearing cause/context chain;
- deterministic fake/in-memory resolver tests;
- strict JSON-safe validation for `ModelRequest.context` and `ModelResponse.metadata`;
- rejection of arbitrary Python objects, including `ProtectedSecret`, from provider transport envelopes;
- rejection of `NaN`/`Infinity` transport values;
- invalid transport input values hidden from Pydantic error strings;
- `Field(default_factory=dict)` used for transport mapping defaults;
- no reverse `xuanmoney.model -> xuanmoney.credentials` dependency;
- `docs/CREDENTIALS.md` and updated provider-contract documentation.

## Preserved architecture

Package direction:

```text
xuanmoney.credentials -> xuanmoney.model
xuanmoney.runtime     -> xuanmoney.model
```

Prohibited reverse dependency:

```text
xuanmoney.model -X-> xuanmoney.credentials
```

Existing runtime/provider path remains:

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge
        -> ModelProvider
        -> provider adapter (future)
```

Runtime invariant remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

Provider configuration remains `max_attempts = 1`.

## Verification

Final PR #12 head:

```text
3640269d2e47551c77bce97e9b8fbccfd4714d54
```

Verification:

- pre-hardening anchor `0ebfee86048a09f1af5d9ab490624c87dd491eba`: PR CI #237 success;
- final transport-hardened head: PR CI #248 success;
- GitHub-hosted `ubuntu-latest` runner;
- Python 3.12;
- branch was ahead of and not behind `main` at final review;
- no unresolved review threads;
- final integration review ID `5096676763` found no remaining architecture or safety blocker;
- squash merge commit: `84edd3e90c9c5c2551e5314410bd7eb554cfe75e`.

## Current limitations

There is still no concrete production credential resolver or real provider integration:

- no real `os.environ` read;
- no secret-manager integration;
- no API-key persistence;
- no OpenAI/Anthropic/Gemini or other provider SDK;
- no external provider network call;
- no provider retry/backoff or fallback;
- no streaming or provider-specific function calling;
- no provider logging/metrics infrastructure;
- no production API/UI;
- no new model-callable tool or financial write capability.

## Recommended next bounded action

**Start `Environment Credential Resolver v0.1` on a fresh feature branch.**

The bounded increment should:

1. implement a concrete application-owned resolver for existing `CredentialSource.ENVIRONMENT` references;
2. accept an injected/read-only mapping so tests never depend on the process environment;
3. optionally provide a narrow application-owned composition helper for `os.environ` only if it does not broaden model/runtime access to environment variables;
4. return only `ProtectedSecret` and never expose raw values through configuration, model transport, runtime results, errors, evidence, or logs;
5. convert missing/unsupported references into the existing sanitized credential-resolution failures without retaining secret-bearing exception chains;
6. use deterministic tests for present, missing, empty, and unsupported values;
7. preserve strict JSON-safe model transport, `max_attempts = 1`, package direction, and the bounded runtime invariant.

Do **not** combine Environment Credential Resolver v0.1 with a real provider SDK, external provider network calls, retry/backoff, fallback, streaming, new analysis tools, or financial write behavior.
