# Canonical Handoff

## Current status

Milestone: **Environment Credential Resolver v0.1**

Status: **READY FOR INTEGRATION — implementation reviewed; final current-head CI required**

Development branch: `feat/environment-credential-resolver-v0.1`

Integration PR: **#14 — `feat: add environment credential resolver v0.1`**

Base: `main@0df388a1a4479ca626ff6fa62240268b0331994b`.

The project is licensed under **Apache License 2.0**.

## Implemented environment resolver

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

Implemented and reviewed:

- `EnvironmentCredentialResolver` implements the existing `CredentialResolver` protocol;
- constructor accepts an injected `Mapping[str, str]`; credential code does not import or read `os.environ`;
- present non-empty values resolve to `ProtectedSecret`;
- missing, empty, non-string, and backing-mapping lookup failures normalize to existing `credential_unavailable`;
- unsupported sources normalize to existing `unsupported_source`;
- lookup failures are normalized after the backing exception handler so sanitized failures retain no cause/context diagnostics;
- resolver `repr` does not expose backing mapping data or credential values;
- deterministic tests use injected mappings and `MappingProxyType`, not host environment contents;
- existing `ProtectedSecret` redaction/non-serialization behavior is reused unchanged.

## Preserved boundaries

Package direction remains:

```text
xuanmoney.credentials -> xuanmoney.model
xuanmoney.runtime     -> xuanmoney.model
xuanmoney.model -X-> xuanmoney.credentials
```

`ModelRequest.context` and `ModelResponse.metadata` remain strict JSON-safe envelopes,
so `ProtectedSecret` cannot enter provider transport payloads.

Existing runtime/provider path remains unchanged:

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

- OpenAI/Anthropic/Gemini or other provider SDKs;
- external provider network calls;
- retry/backoff or provider fallback;
- streaming or provider-specific function calling;
- secret-manager integration or API-key persistence;
- model/runtime/tool/finance direct environment access;
- new model-callable tools;
- SQL/Python/shell/filesystem expansion;
- financial write actions.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

Verified implementation head before this documentation sync:

```text
fd26abe156678faac91e01f2efdeabbe43ee0222
```

- PR CI #267: **success**;
- GitHub-hosted `ubuntu-latest` / Python 3.12;
- PR #14 non-draft and mergeable at review;
- branch `behind_by=0`;
- changed-file audit: 7 files, with production changes limited to `xuanmoney.credentials`;
- no review submissions or unresolved review threads at review time;
- no runtime, finance, tool, dependency, CI, SDK, network, retry/fallback, or financial-write expansion.

This handoff synchronization advances the branch beyond the verified implementation head, so latest current-head CI must also pass before merge.

## Recommended next bounded action

**If latest current-head PR #14 CI is green, record final integration review and squash-merge PR #14.**

After integration, refresh canonical handoff on a documentation-only branch before selecting the next provider-integration boundary.
