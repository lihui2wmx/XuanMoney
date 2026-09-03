# Canonical Handoff

## Current status

Milestone: **OpenAI Provider Adapter v0.1**

Status: **ACTIVE — implementation and deterministic CI baseline complete; integration review pending**

Development branch: `feat/openai-provider-adapter-v0.1`

Integration PR: **#22 — `feat: add OpenAI provider adapter v0.1`**

Base: `main@17de31993172966fa448b0d142ca37a4b6d328ac`.

The preceding readiness/design milestone was integrated through PR #20 and post-merge synchronization PR #21.

The project is licensed under **Apache License 2.0**.

## Implemented provider boundary

```text
ProviderConfiguration(provider_id="openai")
        |
        v
ProviderFactoryRegistry
        |
        v
OpenAIProviderFactory
  # trusted ProtectedSecret.reveal() boundary
        |
        v
OpenAI SDK client
  # timeout=configured seconds
  # max_retries=0
        |
        v
OpenAIProviderAdapter
        |
        v
ModelProvider.complete(ModelRequest)
        |
        +--> prompt -> Responses instructions
        +--> JSON(context) -> Responses input
        |
        v
one synchronous responses.create()
        |
        v
ModelResponse(provider="openai")
        |
        v
ModelPortProviderBridge
        |
        v
BoundedModelRuntime
```

Implemented in PR #22:

- bounded official dependency `openai>=3.7,<4`;
- SDK import confined to application-owned `xuanmoney.providers`;
- one trusted `OpenAIProviderFactory` requiring `provider_id="openai"` and a resolved credential;
- `ProtectedSecret.reveal()` occurs only in trusted SDK client construction;
- SDK client construction applies `request_timeout_seconds` and explicitly sets `max_retries=0`;
- one `OpenAIProviderAdapter.complete()` maps to at most one synchronous `client.responses.create()`;
- existing repository transport contract is preserved: `ModelRequest.prompt -> instructions` and deterministic JSON-safe `ModelRequest.context -> input`;
- the readiness-document mismatch describing nonexistent `ModelRequest.instructions/input` fields is corrected in `docs/OPENAI_PROVIDER_ADAPTER.md` rather than widening `xuanmoney.model`;
- no provider-native `tools`, `stream`, or `background` argument is sent;
- successful nonblank `output_text` maps to `ModelResponse(content=..., provider="openai")` with empty metadata;
- missing/blank output fails closed as `INVALID_RESPONSE`;
- OpenAI authentication/permission, timeout, rate-limit, service, bad-request/configuration, connection, and unexpected exceptions normalize to the existing safe `ProviderFailureCode` taxonomy;
- normalized failures do not retain raw diagnostics, credential material, exception cause, or exception context;
- invalid provider IDs, missing credentials, and invalid SDK client surfaces fail closed;
- deterministic fake-SDK integration executes through registry, injected environment resolver, trusted factory, adapter, `ModelPortProviderBridge`, and `BoundedModelRuntime`.

## Verification

Implementation/test head before documentation synchronization:

```text
26d317d1398b717d15d468288db3dab866231c6c
```

GitHub Actions PR CI #346 passed on GitHub-hosted `ubuntu-latest` / Python 3.12, including installation of the bounded OpenAI SDK dependency and the full deterministic test suite.

The execution container still cannot resolve `github.com`, so no local pytest result is claimed; GitHub-hosted CI remains the executable verification authority for this session.

## Preserved invariants

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
one ModelProvider.complete() call per reached runtime phase
one Responses API call per complete() invocation
```

Package direction remains provider-specific only at the application provider layer. `xuanmoney.model`, runtime, finance, tools, and credentials do not import the OpenAI SDK.

The adapter adds no hidden retry, fallback, alternate model, provider-native tool loop, filesystem/SQL/Python/shell path, or financial write behavior.

## Current limitations

- no live OpenAI network call has been executed;
- no live credential is used in normal tests or CI;
- no second provider exists;
- no streaming or background Responses API mode;
- no provider-native tools/function calling;
- no retry/backoff or provider/model fallback;
- no secret-manager integration;
- no production API/UI;
- no new analysis tool, runtime/finance expansion, or financial write capability.

## Recommended next bounded action

**Complete PR #22 integration review after current-head CI passes.**

The review must confirm:

1. only `xuanmoney.providers` imports `openai`;
2. `max_retries=0` and configured timeout are enforced at client construction;
3. the existing `ModelRequest(prompt, context)` schema remains unchanged;
4. one `complete()` call cannot issue a second provider request;
5. no provider-native tools, streaming, background mode, retry, or fallback surface exists;
6. stable failures and secret non-disclosure hold without retained exception chains;
7. registry/composer/bridge/runtime boundaries remain unchanged;
8. branch remains current/mergeable and current-head GitHub-hosted CI is green.

If those exit conditions hold, integrate PR #22 and perform a documentation-only post-merge synchronization before selecting any new provider/runtime capability.

Do **not** add a second provider, live-network CI, retry/backoff, fallback, streaming, provider-native tool calling, new analysis tools, runtime/finance expansion, or financial write behavior in the integration increment.
