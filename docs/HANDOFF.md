# Canonical Handoff

## Current status

Milestone: **Credential Resolver Boundary v0.1**

Status: **ACTIVE — integration-review hardening applied; current-head CI pending**

Development branch: `feat/credential-resolver-boundary-v0.1`

Integration PR: **#12 — `feat: add credential resolver boundary v0.1`**

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
- fake missing-reference behavior avoids retaining an underlying exception cause/context containing the reference identifier;
- tests proving resolved values remain absent from serialized `ProviderConfiguration`;
- `docs/CREDENTIALS.md` describing the trust and package boundary.

## Integration-review hardening

The first integration review identified that `ProtectedSecret` itself was non-serializable, but the existing provider transport envelopes still used `dict[str, object]`, allowing an arbitrary Python object to be placed into `ModelRequest.context` or `ModelResponse.metadata` before serialization.

The branch therefore adds a package-neutral transport guard in `xuanmoney.model`:

- `ModelRequest.context` and `ModelResponse.metadata` must pass strict standard JSON serialization;
- non-standard `NaN`/`Infinity` values are rejected;
- arbitrary objects, including `ProtectedSecret`, are rejected before entering transport envelopes;
- Pydantic invalid-input values are hidden from validation-error text;
- `Field(default_factory=dict)` replaces mutable dict defaults;
- `xuanmoney.model` does not import `xuanmoney.credentials`, preserving dependency direction.

## Package direction

```text
xuanmoney.credentials -> xuanmoney.model
xuanmoney.model -X-> xuanmoney.credentials
```

Runtime, tools, and finance code do not receive resolved secret values.

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

Pre-hardening implementation anchor `0ebfee86048a09f1af5d9ab490624c87dd491eba` passed PR CI #237 on GitHub-hosted `ubuntu-latest` / Python 3.12.

The transport-hardening commits advance the branch beyond that anchor. Latest current-head CI must pass before integration review can be considered clear.

## Recommended next bounded action

**Run current-head PR #12 CI after transport hardening.**

If green, re-check changed-file scope, package direction, PR threads, secret non-serialization/transport rejection, and sanitized resolver failures. Then mark the branch ready for integration.
