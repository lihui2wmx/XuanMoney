# Provider Configuration & Safety Contract v0.1

## Scope

This milestone defines provider-neutral configuration and failure contracts that must exist before any real external model SDK or network call is introduced.

It does **not** resolve credentials, call a provider, retry requests, add observability infrastructure, or change the bounded runtime execution sequence.

## Configuration contract

`ProviderConfiguration` contains only non-secret values:

- `provider_id`: non-blank provider identifier;
- `model_id`: non-blank model identifier;
- `request_timeout_seconds`: integer from 1 through 120;
- `max_attempts`: fixed to `1`;
- optional `credential_ref`: a non-secret `CredentialReference`.

Unknown fields are rejected.

### Credential references

A `CredentialReference` identifies where a future application-owned resolver may obtain a credential. It does not contain the credential value.

Current supported source:

```text
environment
```

Example safe value:

```json
{
  "source": "environment",
  "identifier": "XUANMONEY_PROVIDER_API_KEY"
}
```

The identifier is a reference name, not the referenced secret. Secret values, API-key values, bearer tokens, passwords, or raw credential payloads must not enter this model.

No credential resolver is implemented in this milestone.

## Retry and timeout policy

The provider configuration contract enforces:

```text
1 <= request_timeout_seconds <= 120
max_attempts = 1
```

`max_attempts` cannot be increased through configuration. There is no automatic provider retry or fallback policy in v0.1.

This preserves the existing runtime invariant:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

A later real provider adapter may use the configured timeout for one network attempt per reached provider phase, but that network behavior is outside this milestone.

## Provider transport failures

`ProviderFailureCode` defines the stable provider-transport taxonomy:

- `invalid_configuration`
- `credential_unavailable`
- `authentication_failed`
- `timeout`
- `rate_limited`
- `service_unavailable`
- `invalid_response`
- `transport_error`

`ProviderFailure` contains the stable code and a message derived only from that code. Provider adapters cannot inject arbitrary public failure text into the model.

Raw provider exceptions, HTTP bodies, stack traces, request payloads, credentials, and secret values are not part of the public failure contract.

`ProviderTransportError` exposes only a `ProviderFailure`. A future adapter must map provider-specific exceptions into one stable code without copying provider diagnostic text into the public exception or serialized failure.

## Trust boundary

```text
application-owned config / future secret resolver
        |
        v
ProviderConfiguration + CredentialReference
        |
        v
future provider adapter
        |
        +--> ProviderTransportError / ProviderFailure
        |
        v
ModelProvider transport
        |
        v
ModelPortProviderBridge
        |
        v
BoundedModelRuntime
```

Secrets remain application-owned and outside serializable provider configuration. Runtime validation and controlled financial-tool execution remain unchanged.

## Explicitly out of scope

- OpenAI, Anthropic, Gemini, or other provider SDK installation;
- API-key values or secret persistence;
- environment-variable reading;
- secret-manager integration;
- external network calls;
- retry/backoff or provider fallback;
- streaming;
- provider-specific function calling;
- logging/metrics infrastructure;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write operations.
