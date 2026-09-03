# Canonical Handoff

## Current status

Milestone: **Provider Adapter Credential Injection v0.1**

Status: **READY FOR INTEGRATION — implementation reviewed; final current-head CI required**

Development branch: `feat/provider-adapter-credential-injection-v0.1`

Integration PR: **#16 — `feat: add provider adapter credential injection v0.1`**

Base: `main@3dc2e5883556048d378b23228d85598a3d620736`, which contains Environment Credential Resolver v0.1 and its post-merge handoff synchronization.

The project is licensed under **Apache License 2.0**.

## Implemented composition boundary

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
              # trusted construction boundary
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

- new application-owned `xuanmoney.providers` package;
- `ProviderAdapterFactory` protocol for trusted provider/client construction;
- `ProviderAdapterComposer` accepting a `CredentialResolver` plus factory;
- optional credential references are resolved exactly once before adapter construction;
- the generic composer never calls `ProtectedSecret.reveal()`;
- only a trusted factory implementation receives `ProtectedSecret` and may explicitly reveal it for client construction;
- unavailable credentials map to sanitized `ProviderFailureCode.CREDENTIAL_UNAVAILABLE`;
- unsupported credential sources map to sanitized `ProviderFailureCode.INVALID_CONFIGURATION`;
- unexpected resolver failures and invalid resolver return types fail closed before factory invocation;
- adapter/factory construction failures normalize to sanitized `ProviderFailureCode.TRANSPORT_ERROR`;
- a factory result without a callable `complete()` surface is rejected immediately as `TRANSPORT_ERROR` rather than leaking into runtime;
- sanitized failures are raised outside source exception handlers so secret-bearing resolver/factory diagnostics are not retained as cause/context chains;
- deterministic fake factory/adapter tests exercise a complete `ModelPortProviderBridge -> BoundedModelRuntime` flow;
- test secret material is absent from provider request serialization, runtime result serialization, public failures, composer/factory/adapter representations, and model-callable payloads;
- `docs/PROVIDER_COMPOSITION.md` defines the trust and package boundary.

## Package direction

Allowed:

```text
xuanmoney.providers   -> xuanmoney.credentials
xuanmoney.providers   -> xuanmoney.model
xuanmoney.credentials -> xuanmoney.model
xuanmoney.runtime     -> xuanmoney.model
```

Forbidden:

```text
xuanmoney.model       -X-> xuanmoney.credentials
xuanmoney.model       -X-> xuanmoney.providers
xuanmoney.credentials -X-> xuanmoney.providers
```

Runtime, tools, and finance code do not receive resolved secret values.

## Preserved runtime/provider policy

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
```

No Finance Kernel, controlled Tool Registry, runtime execution-sequence, provider retry, or financial-write behavior is changed.

## Explicitly out of scope

- OpenAI/Anthropic/Gemini or other vendor SDKs;
- external provider network calls;
- provider-specific HTTP/authentication payloads;
- retry/backoff or provider fallback;
- streaming or provider-specific function calling;
- secret-manager integration or credential persistence;
- provider logging/metrics infrastructure;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write actions.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

Verified implementation head before this final handoff sync:

```text
8b357c947c80eb44adaf2d091f27f3d35aa717fd
```

Verification:

- initial implementation/docs anchor `707523b7744d9fbba47f70fb8e3365c4a331bcb8`: PR CI #284 success;
- fail-closed provider-result hardening head `8b357c947c80eb44adaf2d091f27f3d35aa717fd`: PR CI #294 success;
- GitHub-hosted `ubuntu-latest` / Python 3.12;
- PR #16 non-draft and mergeable at review;
- branch `behind_by=0`;
- changed-file audit: 7 files, with production changes limited to new `xuanmoney.providers` package;
- no review submissions or unresolved review threads at review time;
- no runtime, finance, tool, dependency, SDK, network, retry/fallback, or financial-write expansion.

This handoff synchronization advances the branch beyond the verified implementation head, so latest current-head CI must also pass before merge.

## Recommended next bounded action

**If latest current-head PR #16 CI is green, record final integration review and squash-merge PR #16.**

After integration, refresh canonical handoff on a documentation-only branch before selecting the next vendor-provider boundary.
