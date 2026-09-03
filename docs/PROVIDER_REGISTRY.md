# Controlled Provider Factory Registry v0.1

## Scope

This milestone defines the application-owned provider-factory selection boundary between validated `ProviderConfiguration.provider_id` values and trusted `ProviderAdapterFactory` implementations.

It does not install a vendor SDK, make external provider calls, add retries/fallback, or expose provider selection to model output.

## Boundary

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

## Registry contract

`ProviderFactoryRegistry` receives an explicit iterable of `(provider_id, factory)` entries at construction and snapshots them into an immutable mapping.

Required behavior:

- provider identifiers are strings normalized by surrounding-whitespace stripping and must remain non-blank;
- duplicate identifiers, including duplicates created by normalization, fail closed during construction;
- each factory must expose callable `build(configuration, credential)` behavior;
- unknown configured providers fail closed with sanitized `ProviderFailureCode.INVALID_CONFIGURATION`;
- lookup is driven only by validated application-owned `ProviderConfiguration.provider_id`;
- provider construction delegates to the existing `ProviderAdapterComposer` so credential resolution and failure normalization remain unchanged;
- there is no public `register()` API after construction.

## Forbidden selection mechanisms

The registry must not introduce:

- dynamic imports;
- entry-point or plugin discovery;
- filesystem discovery;
- runtime mutation/registration;
- model-selected factory identifiers outside application configuration;
- fallback to another provider after lookup or construction failure;
- retry-based provider switching.

## Credential safety

The registry itself never receives a raw credential value and never calls `ProtectedSecret.reveal()`.

Credential resolution remains application-owned. A resolved `ProtectedSecret` may be revealed only by the selected trusted `ProviderAdapterFactory` for immediate provider-client/adapter construction. The raw value must not persist in registry/composer/factory/provider representations, provider transport envelopes, runtime results, public failures, logs, or model-callable payloads.

Deterministic integration coverage selects a credential-consuming fake factory through the registry, resolves an injected environment credential, constructs the fake provider through the existing trusted reveal boundary, and executes it through `ModelPortProviderBridge` and `BoundedModelRuntime` while asserting the test secret does not appear in transport or runtime serialization.

## Preserved policy

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
```

The registry does not expand the controlled analysis-tool surface and does not alter finance semantics, runtime execution policy, or provider transport contracts.

## Explicitly out of scope

- OpenAI, Anthropic, Gemini, or other vendor SDKs;
- external provider network calls;
- provider-specific HTTP/auth payloads;
- retry/backoff or provider fallback;
- streaming or provider-specific function calling;
- secret-manager integration or credential persistence;
- dynamic registration/import/plugin discovery;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write operations.
