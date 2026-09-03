# Canonical Handoff

## Current status

Milestone: **Controlled Provider Factory Registry v0.1**

Status: **READY FOR INTEGRATION — implementation, documentation, CI, and integration review complete**

Development branch: `feat/controlled-provider-factory-registry-v0.1`

Integration PR: **#18 — `feat: add controlled provider factory registry v0.1`**

Base: `main@b06ae469c70496a21458b66ecb4878303db25160`.

Reviewed head before this final handoff synchronization:

```text
9322313082cdff06f85a7ad76d8c40310672c0ce
```

PR CI #316 passed on GitHub-hosted `ubuntu-latest` / Python 3.12. Integration review `5096980951` found no remaining architecture, safety, or bounded-scope blocker.

The project is licensed under **Apache License 2.0**.

## Controlled provider selection boundary

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

Implemented and reviewed:

- immutable snapshot-based `ProviderFactoryRegistry` in application-owned `xuanmoney.providers`;
- explicit fixed `provider_id -> ProviderAdapterFactory` allowlist supplied at construction;
- whitespace-normalized non-blank identifiers aligned with `ProviderConfiguration` string semantics;
- duplicate/ambiguous identifiers fail closed during registry construction;
- invalid factories lacking callable `build()` fail closed before credential resolution;
- unknown configured providers fail closed as sanitized `ProviderFailureCode.INVALID_CONFIGURATION` before factory invocation;
- registry selection is driven only by application-owned `ProviderConfiguration.provider_id`;
- selected factories are composed through the existing `ProviderAdapterComposer`;
- no public `register()`, dynamic import, entry-point/plugin/filesystem discovery, model-controlled factory loading, fallback, or retry-based switching;
- deterministic registry-level credential-consuming integration selects a fake factory, resolves an injected environment credential, performs trusted reveal only at factory construction, and executes through `ModelPortProviderBridge` and `BoundedModelRuntime`;
- test secret material remains absent from registry/factory/provider representations, provider request serialization, and runtime result serialization;
- `docs/PROVIDER_REGISTRY.md` documents the selection and credential-safety boundary;
- `docs/DEVELOPMENT_LOG.md` records the active milestone state.

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

- branch base: `main@b06ae469c70496a21458b66ecb4878303db25160`;
- core implementation/test commit `2300791fa062d66203791fc82906973b6a22106c`: PR CI #308 success;
- initial handoff synchronization `df23f502e860d10b07ba89c471b29c474cc4da75`: PR CI #310 success;
- registry credential-consuming integration commit `1a38d0717cfc0468998310cc93d48e5a644cdc1d`;
- milestone documentation added in `docs/PROVIDER_REGISTRY.md` and `docs/DEVELOPMENT_LOG.md`;
- reviewed pre-final-sync head `9322313082cdff06f85a7ad76d8c40310672c0ce`: PR CI #316 success;
- PR #18 is mergeable and `behind_by=0` against `main` at integration review time;
- no review threads are unresolved;
- integration review `5096980951` found no remaining blocker;
- local checkout was unavailable because external DNS resolution for `github.com` failed; no local-test result is claimed.

The final HANDOFF synchronization advances the branch beyond the reviewed head, so current-head GitHub-hosted CI must pass before merge.

## Current limitations

- no real provider factory implementation exists;
- no OpenAI/Anthropic/Gemini or other vendor SDK;
- no external network call or provider-specific HTTP/auth implementation;
- no provider retry/backoff, fallback, streaming, or provider-specific function calling;
- no secret-manager integration or credential persistence;
- no dynamic provider registration/discovery;
- no new model-callable tool, runtime/finance/tool expansion, or financial write capability.

## Recommended next bounded action

**Verify current-head PR CI, then integrate PR #18 if the branch remains current and mergeable.**

After integration, perform a documentation-only post-merge handoff synchronization on `main` before activating any real provider adapter milestone.

Do **not** combine the merge/post-merge synchronization with a vendor SDK, external provider network call, retry/backoff, fallback, streaming, new analysis tools, runtime/finance expansion, or financial write behavior.
