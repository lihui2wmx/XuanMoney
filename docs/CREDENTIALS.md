# Credential Resolver Boundary v0.1

## Scope

This document defines the application-owned credential-resolution boundary from a
non-secret `CredentialReference` to a protected runtime-only secret value. It also
documents the first concrete environment-reference resolver.

The credential layer does not install a provider SDK, make provider network calls, add
retries, or expose secrets to model/runtime/tool/finance payloads.

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
          ProtectedSecret          # runtime-only, opaque/redacted
                  |
                  v
        future provider integration
```

`xuanmoney.model` remains the provider-neutral transport/configuration layer.
`xuanmoney.credentials` may depend on model-layer credential references; the model
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
`ModelRequest`, `ModelResponse`, runtime results, finance evidence, logs, error messages,
or any model-callable payload.

## Model transport guard

`ModelRequest.context` and `ModelResponse.metadata` contain only strict JSON-safe
values. Standard JSON encoding is validated with `NaN`, `Infinity`, and `-Infinity`
disabled. Non-serializable values such as `ProtectedSecret` fail closed before entering
the provider transport contract.

Transport validation hides invalid input values from Pydantic error strings so unsafe
object representations do not become a diagnostic side channel.

This preserves package direction:

```text
xuanmoney.credentials -> xuanmoney.model
xuanmoney.model -X-> xuanmoney.credentials
```

## Resolver protocol

```python
CredentialResolver.resolve(CredentialReference) -> ProtectedSecret
```

Resolvers are application-owned composition components. They expose only a protected
secret or a sanitized credential-resolution failure.

## EnvironmentCredentialResolver

`EnvironmentCredentialResolver` is the first concrete resolver. It supports existing
`CredentialSource.ENVIRONMENT` references and receives the environment data as an
injected `Mapping[str, str]`.

```text
application composition
        |
        +--> Mapping[str, str]
                  |
                  v
EnvironmentCredentialResolver
                  |
                  +--> present non-empty value -> ProtectedSecret
                  |
                  +--> missing/empty/lookup failure -> credential_unavailable
```

The class itself does **not** import or read `os.environ`. A future application
composition root may explicitly pass a process-environment mapping, but that does not
grant environment access to `xuanmoney.model`, runtime, tools, finance code, or the
model-callable surface.

The resolver:

- never returns a raw credential string;
- does not mutate the injected mapping;
- redacts its own representation rather than showing the mapping;
- maps missing and empty values to the existing `credential_unavailable` failure;
- maps unsupported sources to `unsupported_source`;
- normalizes backing-mapping lookup exceptions without preserving their diagnostic
  exception chain;
- does not echo reference identifiers, mapping values, or backing diagnostics in its
  public failures.

Tests use deterministic injected mappings, including `MappingProxyType`, and therefore
do not depend on host environment contents.

## Failure contract

`CredentialResolutionError` exposes only a stable
`CredentialResolutionFailureCode` and a fixed safe message.

Current codes:

- `unsupported_source`
- `credential_unavailable`

Resolver failures must not store or echo:

- credential reference identifiers;
- resolved secret values;
- raw secret-manager or mapping diagnostics;
- environment contents;
- provider request/response data;
- underlying exception chains containing credential reference material.

## Preserved runtime policy

Credential resolution does not alter the model runtime invariant:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

It does not change `max_attempts = 1`, add provider retry/fallback, expand the controlled
tool registry, or introduce financial write behavior.

## Explicitly out of scope

- provider SDKs;
- external provider network calls;
- cloud/local secret-manager integrations;
- API-key persistence;
- retry/backoff or provider fallback;
- streaming or provider-specific function calling;
- logging/metrics infrastructure;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write operations.
