# Credential Resolver Boundary v0.1

## Scope

This milestone defines the application-owned boundary that resolves a non-secret
`CredentialReference` into a protected runtime-only secret value.

It does not read real environment variables, integrate a secret manager, install a
provider SDK, or make a provider network call.

## Boundary

```text
ProviderConfiguration
        |
        +--> CredentialReference   # serializable, non-secret
                  |
                  v
        CredentialResolver         # application-owned
                  |
                  v
          ProtectedSecret           # runtime-only, opaque/redacted
                  |
                  v
        future provider integration
```

`xuanmoney.model` remains the provider-neutral transport/configuration layer.
`xuanmoney.credentials` may depend on the model-layer `CredentialReference`; the model
package must not depend upward on credential resolution.

## ProtectedSecret

`ProtectedSecret` is deliberately not a Pydantic model or serializable configuration
value. It provides an explicit `reveal()` operation for a future trusted provider
integration boundary while keeping normal textual and serialization paths safe.

Required behavior:

- `str(secret)` returns `<redacted>`;
- `repr(secret)` returns `ProtectedSecret(<redacted>)`;
- formatted string output remains redacted;
- JSON serialization fails instead of exposing the value;
- pickle serialization fails instead of persisting the value;
- the wrapper is immutable after construction;
- empty secret values are rejected.

`reveal()` must never be used to place a secret in `ProviderConfiguration`,
`ModelRequest`, runtime results, finance evidence, logs, error messages, or any
model-callable payload.

## Resolver protocol

```python
CredentialResolver.resolve(CredentialReference) -> ProtectedSecret
```

Resolver implementations are application-owned composition components. The production
code in this milestone defines only the protocol and safety contracts. Tests use a
deterministic in-memory fake resolver; no process environment is read.

## Failure contract

`CredentialResolutionError` exposes only a stable
`CredentialResolutionFailureCode` and a fixed safe message.

Current codes:

- `unsupported_source`
- `credential_unavailable`

Resolver failures must not store or echo:

- credential reference identifiers;
- resolved secret values;
- raw secret-manager diagnostics;
- environment contents;
- provider request/response data.

## Preserved runtime policy

Credential resolution does not alter the model runtime invariant:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

It does not change `max_attempts = 1`, add provider retry/fallback, expand the controlled
tool registry, or introduce financial write behavior.

## Explicitly out of scope

- reading `os.environ`;
- cloud/local secret-manager integrations;
- API-key persistence;
- OpenAI/Anthropic/Gemini or any other provider SDK;
- external provider network calls;
- retry/backoff or provider fallback;
- streaming or provider-specific function calling;
- logging/metrics infrastructure;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write operations.
