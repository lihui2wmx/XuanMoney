# Canonical Handoff

## Current status

Milestone: **Credential Resolver Boundary v0.1**

Status: **ACTIVE — implementation and tests added; current-head CI pending**

Development branch: `feat/credential-resolver-boundary-v0.1`

Base: `main` at `63bac1c7025dc7cd712d863e8f144c4e3328bc53`, which contains Provider Configuration & Safety Contract v0.1 and its post-merge handoff synchronization.

The project is licensed under **Apache License 2.0**.

## Implemented credential boundary

The branch adds the application-owned layer between serializable credential references and future real provider integration:

```text
ProviderConfiguration
        |
        +--> CredentialReference            # serializable, non-secret
                  |
                  v
        CredentialResolver                  # xuanmoney.credentials
                  |
                  v
        ProtectedSecret                     # runtime-only, redacted/non-serializable
                  |
                  v
        future provider integration
```

Implemented:

- `CredentialResolver.resolve(CredentialReference) -> ProtectedSecret` protocol;
- `ProtectedSecret` rejecting empty values and immutable after construction;
- `ProtectedSecret.__str__`, `__repr__`, and formatted output are redacted;
- JSON serialization fails instead of exposing the secret;
- pickle serialization fails instead of persisting the secret;
- explicit `reveal()` is the only supported value-extraction operation and is reserved for a future trusted provider integration boundary;
- sanitized `CredentialResolutionFailureCode` values for unsupported source and unavailable credential;
- `CredentialResolutionError` stores only the stable code and fixed safe message, with no credential reference or raw diagnostic payload;
- deterministic fake/in-memory resolver tests for successful and missing-reference paths;
- tests proving resolved values remain absent from serialized `ProviderConfiguration`;
- `docs/CREDENTIALS.md` describing the trust and package boundary.

## Package direction

Credential resolution is application-owned:

```text
xuanmoney.credentials -> xuanmoney.model.CredentialReference
```

`xuanmoney.model` does not depend on `xuanmoney.credentials`. Runtime, tools, and finance code do not receive resolved secret values.

## Preserved architecture and policy

Existing model/runtime path remains unchanged:

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

- reading real environment variables;
- secret-manager integration;
- API-key persistence;
- OpenAI/Anthropic/Gemini or other provider SDK;
- external provider network calls;
- retry/backoff or provider fallback;
- streaming or provider-specific function calling;
- logging/metrics infrastructure;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write actions.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

Current implementation must pass GitHub-hosted `ubuntu-latest` / Python 3.12 CI before integration review.

## Recommended next bounded action

**Open an integration PR for Credential Resolver Boundary v0.1 and run current-head CI.**

If CI is green, perform integration review focused on secret redaction/non-serialization, sanitized resolver failures, package direction, and absence of environment/SDK/network execution before merge.
