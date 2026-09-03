# Canonical Handoff

## Current status

Milestone: **Controlled Provider Factory Registry v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `73f7cbb5ffeeeaa79204d5c38f12e2e1c47f6b56`

Merged PR: **#18 — `feat: add controlled provider factory registry v0.1`**

Final PR head: `4cc6d621c9296cff5424ae13f95b0607a20cb931`

PR CI #320 passed on GitHub-hosted `ubuntu-latest` / Python 3.12. Integration review `5096980951` found no remaining architecture, safety, or bounded-scope blocker.

The project is licensed under **Apache License 2.0**.

## Integrated provider selection boundary

```text
ProviderConfiguration
        |
        v
ProviderFactoryRegistry
  # fixed application-owned allowlist
        |
        v
ProviderAdapterFactory
        |
        v
ProviderAdapterComposer
        |
        +--> CredentialResolver -> ProtectedSecret
        |
        v
trusted factory reveal/construction boundary
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

Integrated through PR #18:

- immutable snapshot-based `ProviderFactoryRegistry` in application-owned `xuanmoney.providers`;
- explicit fixed `provider_id -> ProviderAdapterFactory` allowlist;
- whitespace-normalized, non-blank provider identifiers aligned with `ProviderConfiguration` semantics;
- duplicate/ambiguous identifiers fail closed during registry construction;
- invalid factories lacking callable `build()` fail closed before credential resolution;
- unknown configured providers fail closed as sanitized `ProviderFailureCode.INVALID_CONFIGURATION` before factory invocation;
- provider selection is driven only by application-owned `ProviderConfiguration.provider_id`;
- selected factories are composed through the existing `ProviderAdapterComposer`;
- no public `register()`, dynamic import, entry-point/plugin/filesystem discovery, model-controlled factory loading, fallback, or retry-based switching;
- deterministic credential-consuming integration selects a fake factory, resolves an injected environment credential, performs trusted reveal only at factory construction, and executes through `ModelPortProviderBridge` and `BoundedModelRuntime`;
- test secret material remains absent from registry/factory/provider representations, provider request serialization, and runtime result serialization;
- `docs/PROVIDER_REGISTRY.md` documents the selection and credential-safety boundary.

## Preserved boundaries

Allowed package direction remains:

```text
xuanmoney.providers   -> xuanmoney.credentials
xuanmoney.providers   -> xuanmoney.model
xuanmoney.credentials -> xuanmoney.model
xuanmoney.runtime     -> xuanmoney.model
```

Forbidden reverse dependencies remain:

```text
xuanmoney.model       -X-> xuanmoney.credentials
xuanmoney.model       -X-> xuanmoney.providers
xuanmoney.credentials -X-> xuanmoney.providers
```

The registry is not model-callable and does not receive model output. Credential reveal remains confined to a trusted `ProviderAdapterFactory`; registry and generic composition code never call `ProtectedSecret.reveal()`.

Runtime/provider policy remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
```

## Verification

- final feature head `4cc6d621c9296cff5424ae13f95b0607a20cb931`: GitHub-hosted PR CI #320 success;
- branch was `behind_by=0` and PR was mergeable immediately before merge;
- no unresolved review threads;
- integration review `5096980951` found no remaining blocker;
- squash merge commit: `73f7cbb5ffeeeaa79204d5c38f12e2e1c47f6b56`;
- no local-test result is claimed because the execution environment could not resolve `github.com`; GitHub-hosted CI is the executable verification authority for this session.

## Current limitations

- no real provider factory implementation exists;
- no OpenAI/Anthropic/Gemini or other vendor SDK is installed;
- no external model-provider network call exists;
- no provider-specific HTTP/auth request translation exists;
- no retry/backoff or provider fallback;
- no streaming or provider-specific function/tool calling;
- no secret-manager integration or credential persistence;
- no production API/UI;
- no new model-callable tool, runtime/finance/tool expansion, or financial write capability.

## Recommended next bounded action

**Perform a First Real Provider Adapter v0.1 readiness/design review before implementation.**

The review should select exactly one provider target and define:

1. the concrete SDK/client dependency and minimal dependency footprint;
2. how `ProviderConfiguration.model_id` and `request_timeout_seconds` map into one provider request;
3. how a trusted factory consumes `ProtectedSecret` only for client/auth construction;
4. translation from `ModelRequest` to provider-specific request payload and back to `ModelResponse`;
5. mapping of provider-specific authentication, timeout, rate-limit, service, invalid-response, and transport failures into existing stable `ProviderFailureCode` values without diagnostic leakage;
6. tests that use deterministic fakes/mocks before any live credential or network integration;
7. explicit preservation of `max_attempts = 1`, no fallback, no streaming, no provider-native autonomous tool loop, and the bounded runtime invariant.

Do **not** implement multiple providers, retry/backoff, fallback, streaming, provider-specific tool calling, new analysis tools, runtime/finance expansion, or financial write behavior in the readiness/design increment.
