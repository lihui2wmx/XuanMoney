# Canonical Handoff

## Current status

Milestone: **Controlled Provider Factory Registry v0.1**

Status: **ACTIVE — core registry implemented and PR CI verified**

Development branch: `feat/controlled-provider-factory-registry-v0.1`

Integration PR: **#18 — `feat: add controlled provider factory registry v0.1`**

Base: `main@b06ae469c70496a21458b66ecb4878303db25160`.

Verified implementation head before this handoff update:

```text
2300791fa062d66203791fc82906973b6a22106c
```

PR CI #308 passed on GitHub-hosted `ubuntu-latest` / Python 3.12.

The project is licensed under **Apache License 2.0**.

## Active provider selection boundary

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
        +------------------------+
        |                        |
        v                        v
ProviderAdapterComposer   CredentialResolver
        |                        |
        +-----------+------------+
                    v
             ProtectedSecret
                    |
                    v
             trusted factory
        # reveal/construction boundary
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

Implemented in the current increment:

- immutable snapshot-based `ProviderFactoryRegistry` in application-owned `xuanmoney.providers`;
- explicit `provider_id -> ProviderAdapterFactory` allowlist supplied at construction;
- provider identifiers use the same whitespace-normalized, non-blank semantics as `ProviderConfiguration`;
- duplicate identifiers, including duplicates created by whitespace normalization, fail closed at registry construction;
- invalid factory objects lacking callable `build()` fail closed at construction;
- unknown configured provider identifiers fail closed as sanitized `ProviderFailureCode.INVALID_CONFIGURATION` before any factory invocation;
- `build()` selects only from `ProviderConfiguration.provider_id` and delegates construction through the existing `ProviderAdapterComposer`;
- registry has no public `register()` method and no dynamic import, plugin, entry-point, filesystem, or model-controlled discovery path;
- deterministic tests cover selection, unknown providers, duplicate/invalid identifiers, invalid factories, snapshot immutability, and lack of registration surface.

## Preserved trust and runtime boundaries

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

The registry does not receive model output and does not expose provider selection as a model-callable tool.

Credential reveal remains confined to a trusted `ProviderAdapterFactory`; registry and generic composition code never call `ProtectedSecret.reveal()`.

Runtime policy remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
```

## Verification

- branch created from `main@b06ae469c70496a21458b66ecb4878303db25160`;
- implementation/test commit: `2300791fa062d66203791fc82906973b6a22106c`;
- PR #18 opened against `main`;
- GitHub Actions CI run #308 / run ID `33705207540`: **success**;
- test job including the new registry tests: **success**;
- local checkout was unavailable in the execution environment because external DNS resolution for `github.com` failed; no local-test result is claimed.

## Current limitations

- current registry tests exercise the existing composer with configurations that do not require credentials; the prior composer milestone separately covers credential reveal confinement;
- no registry-level credential-consuming end-to-end test yet proves that selection plus credential resolution plus trusted reveal remains non-leaking in one path;
- milestone-specific architecture documentation and development-log synchronization are not yet complete;
- no real provider factory implementation exists;
- no OpenAI/Anthropic/Gemini or other vendor SDK;
- no external network call, provider-specific HTTP/auth implementation, retry/backoff, fallback, streaming, or provider-specific function calling;
- no new model-callable tool or financial write capability.

## Recommended next bounded action

**Add registry-level credential-consuming integration coverage and milestone documentation, without introducing a vendor SDK.**

The next increment should:

1. select a deterministic credential-consuming fake factory by `ProviderConfiguration.provider_id` through `ProviderFactoryRegistry`;
2. resolve an injected environment credential and construct the fake provider through the existing trusted reveal boundary;
3. execute the selected provider through `ModelPortProviderBridge` and `BoundedModelRuntime`;
4. prove secret material is absent from registry/composer/factory/provider representations, provider transport serialization, runtime results, and public failures;
5. document the controlled registry boundary and synchronize `docs/DEVELOPMENT_LOG.md`;
6. rerun GitHub-hosted PR CI and then perform integration review.

Do **not** add vendor SDKs, external network calls, dynamic registration/import/discovery, retry/backoff, provider fallback, streaming, new analysis tools, runtime/finance expansion, or financial write behavior.
