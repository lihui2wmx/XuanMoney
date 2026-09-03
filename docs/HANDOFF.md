# Canonical Handoff

## Current status

Milestone: **Provider Adapter Credential Injection v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `572ac05873ba3ff3cebd182fc72d07bb2f2dec65`

Merged PR: **#16 — `feat: add provider adapter credential injection v0.1`**

The project is licensed under **Apache License 2.0**.

## Integrated provider composition boundary

```text
ProviderConfiguration              CredentialResolver
        |                                 |
        |                                 v
        |                         ProtectedSecret
        |                                 |
        +---------------+-----------------+
                        v
              ProviderAdapterComposer
                        |
                        v
              ProviderAdapterFactory
              # trusted reveal/construction boundary
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

Integrated through PR #16:

- application-owned `xuanmoney.providers` package;
- `ProviderAdapterFactory` protocol for trusted provider/client construction;
- `ProviderAdapterComposer` combines existing provider configuration and credential-resolution contracts;
- configured credentials resolve once to `ProtectedSecret` before adapter construction;
- generic composition code never calls `ProtectedSecret.reveal()`;
- explicit secret reveal is confined to a trusted factory/client-construction implementation;
- unavailable credentials normalize to sanitized `ProviderFailureCode.CREDENTIAL_UNAVAILABLE`;
- unsupported credential sources normalize to `ProviderFailureCode.INVALID_CONFIGURATION`;
- unexpected resolver failures and invalid resolver return values fail closed before factory invocation;
- adapter/factory construction failures normalize to sanitized `ProviderFailureCode.TRANSPORT_ERROR` without retaining raw cause/context diagnostics;
- factory results without a callable `complete()` surface fail closed at composition time;
- deterministic fake adapter/factory tests execute through `ModelPortProviderBridge` and `BoundedModelRuntime`;
- test credential material remains absent from provider request serialization, runtime result serialization, public failures, and object representations;
- `docs/PROVIDER_COMPOSITION.md` documents the trusted reveal and failure-normalization boundary.

## Preserved package and runtime boundaries

Allowed dependency direction:

```text
xuanmoney.providers   -> xuanmoney.credentials
xuanmoney.providers   -> xuanmoney.model
xuanmoney.credentials -> xuanmoney.model
xuanmoney.runtime     -> xuanmoney.model
```

Forbidden reverse dependencies:

```text
xuanmoney.model       -X-> xuanmoney.credentials
xuanmoney.model       -X-> xuanmoney.providers
xuanmoney.credentials -X-> xuanmoney.providers
```

Runtime invariant remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

Provider configuration remains `max_attempts = 1`.

## Verification

Final PR #16 head:

```text
9c1e5dbc47931c5cc0720811a3c5799e7a575fca
```

Verification:

- initial implementation/docs anchor `707523b7744d9fbba47f70fb8e3365c4a331bcb8`: PR CI #284 success;
- invalid-provider-result hardening head `8b357c947c80eb44adaf2d091f27f3d35aa717fd`: PR CI #294 success;
- final canonical-doc synchronized head: PR CI #298 success;
- GitHub-hosted `ubuntu-latest` / Python 3.12;
- final branch was `behind_by=0` and PR mergeable;
- no unresolved review threads;
- final integration review ID `5096853542` found no remaining architecture or safety blocker;
- squash merge commit: `572ac05873ba3ff3cebd182fc72d07bb2f2dec65`.

## Current limitations

There is still no controlled provider-factory selection or real external model provider implementation:

- callers currently inject a `ProviderAdapterFactory` directly into `ProviderAdapterComposer`;
- no fixed `provider_id -> factory` registry exists;
- no OpenAI/Anthropic/Gemini or other vendor SDK;
- no external provider network call;
- no provider-specific HTTP/auth payload implementation;
- no provider retry/backoff or fallback;
- no streaming or provider-specific function calling;
- no secret-manager integration or credential persistence;
- no production API/UI;
- no new model-callable tool or financial write capability.

## Recommended next bounded action

**Start `Controlled Provider Factory Registry v0.1` on a fresh feature branch.**

The bounded increment should:

1. define an immutable application-owned registry mapping validated `provider_id` strings to trusted `ProviderAdapterFactory` implementations;
2. expose lookup/build behavior without a public dynamic `register()` API;
3. reject unknown provider identifiers with a stable sanitized `ProviderFailureCode.INVALID_CONFIGURATION` failure;
4. ensure provider selection occurs from application configuration only, never from model output or model-callable tool arguments;
5. prohibit dynamic imports, entry-point/plugin discovery, filesystem discovery, fallback to another provider, or retry-based provider switching;
6. compose the selected factory through the existing `ProviderAdapterComposer` and deterministic fake resolver/factory tests;
7. prove duplicate/ambiguous provider identifiers fail closed at registry construction;
8. preserve credential reveal confinement, JSON-safe model transport, `max_attempts = 1`, and the bounded runtime invariant;
9. keep vendor SDKs and external network calls out of this milestone.

Do **not** combine this milestone with OpenAI/Anthropic/Gemini SDK installation, external provider calls, retry/backoff, fallback, streaming, new analysis tools, or financial write behavior.
