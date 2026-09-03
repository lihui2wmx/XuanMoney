# Canonical Handoff

## Current status

Milestone: **Environment Credential Resolver v0.1**

Status: **ACTIVE — implementation and deterministic tests added; PR CI pending**

Development branch: `feat/environment-credential-resolver-v0.1`

Base: `main@0df388a1a4479ca626ff6fa62240268b0331994b`.

The project is licensed under **Apache License 2.0**.

## Implemented environment resolver

The active branch adds the first concrete application-owned credential resolver:

```text
application composition
        |
        +--> injected Mapping[str, str]
                  |
                  v
EnvironmentCredentialResolver
                  |
                  +--> CredentialReference(environment)
                  |
                  v
ProtectedSecret
                  |
                  v
future trusted provider integration
```

Implemented:

- `EnvironmentCredentialResolver` implements the existing `CredentialResolver` protocol;
- constructor accepts an injected `Mapping[str, str]` and the credential package does not import or read `os.environ`;
- present non-empty values resolve to `ProtectedSecret`;
- missing and empty values normalize to existing `credential_unavailable` failures;
- unsupported sources normalize to existing `unsupported_source` failures;
- backing-mapping lookup exceptions are sanitized without retaining cause/context diagnostics;
- resolver `repr` does not expose the backing mapping or credential values;
- deterministic tests use injected mappings and `MappingProxyType`, never host environment contents;
- existing `ProtectedSecret` redaction/non-serialization behavior is reused unchanged.

## Preserved credential and transport boundary

```text
ProviderConfiguration
        -> CredentialReference          # serializable, non-secret
        -> EnvironmentCredentialResolver
        -> ProtectedSecret              # runtime-only, redacted/non-serializable
```

Package direction remains:

```text
xuanmoney.credentials -> xuanmoney.model
xuanmoney.runtime     -> xuanmoney.model
xuanmoney.model -X-> xuanmoney.credentials
```

`ModelRequest.context` and `ModelResponse.metadata` remain strict JSON-safe envelopes,
so `ProtectedSecret` cannot enter provider transport payloads.

Existing runtime/provider path is unchanged:

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge
        -> ModelProvider
        -> provider adapter (future)
```

Runtime invariant remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

Provider configuration remains `max_attempts = 1`.

## Explicitly out of scope

- no OpenAI/Anthropic/Gemini or other provider SDK;
- no external provider network calls;
- no retry/backoff or provider fallback;
- no streaming or provider-specific function calling;
- no secret-manager integration;
- no API-key persistence;
- no model/runtime/tool/finance direct environment access;
- no new model-callable tools;
- no SQL/Python/shell/filesystem expansion;
- no financial write actions.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

Current implementation must pass GitHub-hosted PR CI on `ubuntu-latest` / Python 3.12 before integration review.

## Recommended next bounded action

**Open the integration PR and run current-head CI.**

If green, review changed-file scope, package direction, resolver failure sanitization, mapping/repr non-disclosure, and absence of runtime/provider-SDK expansion. Only then mark the branch ready for integration.
