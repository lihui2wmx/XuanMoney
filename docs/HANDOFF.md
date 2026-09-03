# Canonical Handoff

## Current status

Milestone: **Environment Credential Resolver v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `67c957eb199efc8ee8b7c8955635e667237b58f7`

Merged PR: **#14 — `feat: add environment credential resolver v0.1`**

The project is licensed under **Apache License 2.0**.

## Integrated environment resolver

```text
application composition
        |
        +--> injected Mapping[str, str]
                  |
                  v
EnvironmentCredentialResolver
                  |
                  +--> CredentialReference(environment)
                  |
                  v
ProtectedSecret
                  |
                  v
future trusted provider integration
```

Integrated through PR #14:

- `EnvironmentCredentialResolver` implements the existing `CredentialResolver` protocol;
- constructor accepts an injected `Mapping[str, str]`; the credential package does not import or read `os.environ`;
- present non-empty values resolve to `ProtectedSecret` only;
- missing, empty, non-string, and backing-mapping lookup failures normalize to existing `credential_unavailable`;
- unsupported sources normalize to existing `unsupported_source`;
- backing-mapping lookup failures are normalized without retaining raw diagnostic cause/context chains;
- resolver representation does not expose the backing mapping or credential values;
- deterministic tests use injected mappings and `MappingProxyType`, not host environment contents;
- existing `ProtectedSecret` redaction/non-serialization behavior is unchanged.

## Preserved boundaries

Package direction remains:

```text
xuanmoney.credentials -> xuanmoney.model
xuanmoney.runtime     -> xuanmoney.model
xuanmoney.model -X-> xuanmoney.credentials
```

`ModelRequest.context` and `ModelResponse.metadata` remain strict JSON-safe envelopes,
so `ProtectedSecret` cannot enter provider transport payloads.

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

Final PR #14 head:

```text
7646a1d38e105aeb844bba01a96dc0395988273d
```

Verification:

- implementation head `fd26abe156678faac91e01f2efdeabbe43ee0222`: PR CI #267 success;
- final documentation-synchronized head: PR CI #269 success;
- GitHub-hosted `ubuntu-latest` / Python 3.12;
- PR was non-draft and mergeable at final review;
- branch was `behind_by=0`;
- no unresolved review threads;
- final integration review ID `5096782358` found no remaining architecture or safety blocker;
- squash merge commit: `67c957eb199efc8ee8b7c8955635e667237b58f7`.

## Current limitations

There is still no real external model provider integration:

- no provider adapter consumes resolved credentials yet;
- no OpenAI/Anthropic/Gemini or other provider SDK;
- no external provider network call;
- no provider retry/backoff or fallback;
- no streaming or provider-specific function calling;
- no secret-manager integration or API-key persistence;
- no production API/UI;
- no new model-callable tool or financial write capability.

## Recommended next bounded action

**Start `Provider Adapter Credential Injection v0.1` on a fresh feature branch.**

The bounded increment should:

1. define an application-owned adapter-construction/composition boundary that accepts existing `ProviderConfiguration` plus a `CredentialResolver`;
2. resolve an optional `CredentialReference` through the resolver and keep `ProtectedSecret` outside all serializable configuration/model/runtime payloads;
3. confine any explicit `ProtectedSecret.reveal()` operation to the trusted adapter-construction/client boundary;
4. use a deterministic fake provider client/adapter to prove the credential can be consumed without appearing in `ModelRequest`, `ModelResponse`, runtime results, evidence, exceptions, reprs, or test snapshots;
5. normalize credential-resolution failure before adapter construction without fallback/retry;
6. preserve `max_attempts = 1`, JSON-safe provider transport, package direction, and the bounded runtime invariant;
7. keep vendor SDKs and external network calls out of this milestone.

Do **not** combine this milestone with OpenAI/Anthropic/Gemini SDK installation, external provider calls, retry/backoff, fallback, streaming, new analysis tools, or financial write behavior.
