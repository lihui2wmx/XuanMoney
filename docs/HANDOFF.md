# Canonical Handoff

## Current status

Milestone: **ModelPort Provider Bridge v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `b6614b7f207fe6d594c8472758a053c85668bae6`

Merged PR: **#8 — `feat: add model port provider bridge v0.1`**

The project is licensed under **Apache License 2.0**.

## Integrated model/provider path

The repository now contains the complete provider-neutral path from bounded runtime orchestration to a lower-level provider transport contract:

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge   # xuanmoney.runtime
        -> ModelProvider             # xuanmoney.model
        -> Provider Adapter
        -> external model service (future)
```

`ModelPortProviderBridge`:

- creates exactly one typed provider request for each reached planning/synthesis phase;
- carries the serialized typed runtime request and copied response JSON Schema;
- calls `ModelProvider.complete()` exactly once per reached phase;
- strictly JSON-decodes provider content;
- rejects malformed JSON and non-standard `NaN`/`Infinity` numeric constants;
- returns decoded output as untrusted data for existing runtime validation;
- contains no retry, fallback, alternate tool/provider selection, or financial execution logic.

## Preserved runtime and package boundaries

The runtime invariant remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

`BoundedModelRuntime` remains responsible for planner/synthesis validation, controlled-tool enforcement, terminal failure classification, and provider-exception sanitization.

Package dependency direction is:

```text
xuanmoney.runtime.provider_bridge -> xuanmoney.model
```

`xuanmoney.model` remains lower-level provider transport and does not depend on runtime, tools, or finance execution modules.

## Verification

Final PR #8 branch head:

```text
427b9083b206fa8abb7b97d9cb1f3b558c957f2d
```

Verification:

- final PR CI #181: **success**;
- GitHub-hosted `ubuntu-latest` runner;
- Python 3.12;
- branch was ahead of and not behind `main` at final review;
- no unresolved review threads/comments;
- squash merge commit: `b6614b7f207fe6d594c8472758a053c85668bae6`.

## Current limitations

There is still no real external model-provider integration. Specifically:

- no OpenAI/Anthropic/Gemini or other provider SDK;
- no provider credentials or secret-resolution mechanism;
- no external model network call;
- no provider timeout/rate-limit configuration contract;
- no provider observability/redaction contract beyond existing runtime exception sanitization;
- no streaming or provider-specific function calling;
- no provider retry/fallback policy;
- no production API/UI.

## Recommended next bounded action

**Start `Provider Configuration & Safety Contract v0.1` on a fresh feature branch.**

The increment should define and test, without a real provider SDK or network call:

1. typed provider-neutral, non-secret configuration (provider/model identifiers and bounded request timeout);
2. a credential-reference type that identifies a credential source without containing, serializing, or logging the secret value itself;
3. explicit `max_attempts = 1` / no automatic provider retry policy consistent with the current runtime invariant;
4. a stable provider transport failure taxonomy whose public/serialized form contains no raw provider diagnostic or credential material;
5. deterministic fake-provider/config tests for invalid timeout/configuration, secret non-serialization, and sanitized failure behavior;
6. documentation of the trust boundary before any real provider SDK is introduced.

Do **not** combine this increment with OpenAI/Anthropic/Gemini SDK installation, API keys, network calls, streaming, new model-callable tools, or financial write behavior.
