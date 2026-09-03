# Provider Adapter Credential Injection v0.1

## Scope

This milestone defines the application-owned composition boundary that combines an
existing `ProviderConfiguration` with a `CredentialResolver` before constructing a
provider adapter.

It does not install a vendor SDK, create a real provider client, or make any network
request.

## Boundary

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
```

`ProviderAdapterComposer` resolves credentials but deliberately never calls
`ProtectedSecret.reveal()`. The explicit reveal operation belongs only to a trusted
`ProviderAdapterFactory` / provider-client construction implementation.

## Package direction

The application-owned provider-composition package may depend on both lower-level
contracts:

```text
xuanmoney.providers   -> xuanmoney.credentials
xuanmoney.providers   -> xuanmoney.model
xuanmoney.credentials -> xuanmoney.model
```

Forbidden reverse dependencies remain:

```text
xuanmoney.model       -X-> xuanmoney.credentials
xuanmoney.model       -X-> xuanmoney.providers
xuanmoney.credentials -X-> xuanmoney.providers
```

Runtime code continues to depend only on `ModelProvider` through the existing
`ModelPortProviderBridge`; it does not receive resolved credentials.

## Composition contract

`ProviderAdapterFactory.build()` receives:

- the immutable, serializable `ProviderConfiguration`;
- a `ProtectedSecret` when `credential_ref` is configured, otherwise `None`.

The factory is the trusted boundary that may call `credential.reveal()` solely to
construct a provider client/adapter. It must not persist or expose the raw value in:

- adapter/factory representation;
- `ModelRequest` / `ModelResponse`;
- runtime results;
- finance evidence;
- exceptions or diagnostics;
- model-callable payloads;
- logs or snapshots.

The generic composer never handles the raw string value.

## Failure behavior

Credential resolution occurs exactly once when a credential reference is configured.
Adapter construction occurs exactly once after successful resolution.

Failures are normalized without retry or fallback:

- unavailable credential -> `ProviderFailureCode.CREDENTIAL_UNAVAILABLE`;
- unsupported credential source -> `ProviderFailureCode.INVALID_CONFIGURATION`;
- unexpected resolver failure -> `ProviderFailureCode.CREDENTIAL_UNAVAILABLE`;
- adapter/factory construction failure -> `ProviderFailureCode.TRANSPORT_ERROR`.

The public error is a fresh sanitized `ProviderTransportError`. Raw resolver/factory
exceptions are not retained as `__cause__` or `__context__` chains.

## Verification strategy

Deterministic tests use an injected environment mapping plus a fake provider factory.
The fake factory is the only test component that explicitly reveals the credential. It
consumes the raw value during adapter construction and stores only non-secret state.

The composed fake adapter is then exercised through:

```text
ProviderAdapterComposer
        -> ModelProvider
        -> ModelPortProviderBridge
        -> BoundedModelRuntime
```

Tests assert the fake secret is absent from provider transport requests, runtime result
serialization, public failures, and object representations.

## Preserved policy

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
```

This milestone adds no retry/backoff, provider fallback, streaming, new model-callable
tool, unrestricted SQL/Python/shell/filesystem access, or financial write behavior.

## Explicitly out of scope

- OpenAI/Anthropic/Gemini or other vendor SDKs;
- external provider network calls;
- provider-specific authentication headers or HTTP payloads;
- retry/backoff or provider fallback;
- streaming/function-calling provider behavior;
- secret-manager integration or credential persistence;
- provider logging/metrics infrastructure;
- production API/UI;
- new analysis tools or financial write operations.
