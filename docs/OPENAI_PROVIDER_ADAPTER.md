# OpenAI Provider Adapter v0.1 Readiness Design

## Decision

The first real provider target is **OpenAI Responses API** through the official Python `openai` package.

This document is a readiness/design boundary only. It does not install the SDK, construct a live client, read a live credential, or send a network request.

## Why OpenAI first

The existing provider contract is synchronous and intentionally narrow:

```text
ModelProvider.complete(ModelRequest) -> ModelResponse
```

A single synchronous `client.responses.create(...)` request maps cleanly onto that contract without adding streaming, provider-native tool execution, retry loops, or a second runtime state machine.

The initial implementation should use the official `openai` Python package and the Responses API only. No Chat Completions compatibility path should be added in the same milestone.

## Dependency boundary

Implementation milestone target dependency:

```text
openai>=3.7,<4
```

The implementation milestone must add only the official SDK dependency required for the adapter. It must not add a separate HTTP client dependency unless the SDK contract demonstrably requires one for the selected implementation.

The SDK is application/provider-layer infrastructure. `xuanmoney.model`, `xuanmoney.runtime`, `xuanmoney.finance`, and `xuanmoney.tools` must not import `openai`.

## Provider identifier

The controlled registry identifier for this adapter is:

```text
openai
```

Selection remains application-owned through `ProviderConfiguration.provider_id`. Model output and model-callable tool arguments must never select or alter the provider.

## Trusted construction boundary

A future `OpenAIProviderFactory` belongs under application-owned `xuanmoney.providers`.

The factory may receive:

- validated `ProviderConfiguration`;
- `ProtectedSecret | None` from the existing composer.

For `provider_id="openai"`, a credential is required. The factory is the only new component permitted to call `ProtectedSecret.reveal()`.

The raw value may be passed directly into the official SDK client constructor as the API key, but must not be stored separately on the factory or adapter and must never enter repr/str, exceptions, metadata, prompts, evidence, logs, or test snapshots.

Client construction policy:

```text
OpenAI(
    api_key=<revealed credential>,
    timeout=configuration.request_timeout_seconds,
    max_retries=0,
)
```

`max_retries=0` is mandatory because repository policy fixes provider attempts to one. SDK defaults must not silently widen that invariant.

## Request mapping

`ProviderConfiguration.model_id` maps directly to the Responses API `model` parameter.

Each `ModelRequest` maps to exactly one Responses API call.

Initial mapping:

```text
ModelRequest.instructions -> Responses API instructions
ModelRequest.input        -> Responses API input
ProviderConfiguration.model_id -> model
ProviderConfiguration.request_timeout_seconds -> request/client timeout
```

No provider-native tools are supplied. No web search, file search, computer use, shell, code interpreter, function calling, MCP, or other built-in/custom tool surface is enabled by this adapter milestone.

The adapter must not reinterpret finance semantics or runtime planning/synthesis contracts. It transports the already-prepared request only.

## Response mapping

The adapter returns one `ModelResponse`.

For v0.1:

- response text is extracted from the SDK response's canonical text output surface;
- blank/missing/unusable text fails closed as `ProviderFailureCode.INVALID_RESPONSE`;
- `ModelResponse.provider` is the stable string `openai`;
- `ModelResponse.metadata` remains minimal and JSON-safe;
- provider request IDs or other non-secret stable identifiers may be considered later, but are not required for v0.1.

Raw SDK response objects must not be embedded in `ModelResponse.metadata`.

## Failure normalization

Provider-specific exceptions are translated into the existing stable taxonomy without preserving raw exception text, response bodies, headers, request payloads, API keys, or exception cause/context chains.

Required mapping:

```text
OpenAI authentication/permission credential failures -> AUTHENTICATION_FAILED
OpenAI timeout exception                           -> TIMEOUT
OpenAI rate-limit exception                        -> RATE_LIMITED
OpenAI >=500/service-unavailable class             -> SERVICE_UNAVAILABLE
OpenAI connection/transport exception              -> TRANSPORT_ERROR
missing/unusable response text                     -> INVALID_RESPONSE
unexpected SDK/client exception                    -> TRANSPORT_ERROR
```

Bad-request/model-configuration errors that arise from application-owned provider/model configuration should fail closed as `INVALID_CONFIGURATION` where the SDK exposes a reliably classifiable configuration/request error. The implementation must not leak the provider's diagnostic text to decide or explain the public failure.

All public failures remain `ProviderTransportError` with code-derived safe messages only.

## Runtime invariants

The implementation must preserve:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
one ModelProvider.complete() call per reached runtime phase
```

The adapter must not add:

- SDK automatic retries;
- application retry/backoff;
- provider fallback;
- alternate model fallback;
- streaming;
- provider-native autonomous tool loops;
- provider-native function/tool invocation;
- hidden filesystem/SQL/Python/shell access.

## Deterministic test strategy

No live API key or network request is required for the implementation milestone's acceptance tests.

Tests should inject or monkeypatch a deterministic fake SDK client/factory boundary and prove:

1. registry selects only `provider_id="openai"` for the OpenAI factory;
2. trusted factory reveals the `ProtectedSecret` only for client construction;
3. client construction receives `max_retries=0` and the configured timeout;
4. `model_id`, instructions, and input map exactly once into one Responses API request;
5. successful SDK text maps to `ModelResponse`;
6. authentication, timeout, rate-limit, service, invalid-response, and generic transport failures normalize to stable codes;
7. raw provider diagnostics and credential material are absent from public errors and object representations;
8. the adapter executes through `ModelPortProviderBridge` and `BoundedModelRuntime` using deterministic fake SDK responses;
9. no retry or second provider call occurs after a provider failure;
10. no provider-native tool surface is sent to the SDK.

A later optional live smoke test may be designed separately and must not be part of normal CI or require repository secrets by default.

## Implementation shape

Recommended bounded implementation files:

```text
src/xuanmoney/providers/openai_adapter.py
src/xuanmoney/providers/__init__.py
pyproject.toml
tests/test_openai_provider_adapter.py
docs/HANDOFF.md
docs/DEVELOPMENT_LOG.md
```

Do not modify finance kernels, controlled analysis tools, runtime state transitions, model transport schemas, credential resolver semantics, or registry mutation policy unless a concrete incompatibility is found and reviewed first.

## Exit conditions for OpenAI Provider Adapter v0.1

The implementation milestone is complete only when:

- official `openai` SDK dependency is bounded;
- one trusted `OpenAIProviderFactory` and one provider adapter implement the existing contracts;
- SDK retries are explicitly disabled;
- configured timeout and model ID are applied;
- credential reveal remains confined to trusted client construction;
- one `ModelRequest` produces at most one SDK request;
- successful text response produces a valid `ModelResponse`;
- stable failure mappings are covered deterministically;
- no raw provider diagnostics/secrets leak through public failures, transport, runtime results, or repr;
- deterministic bridge/runtime integration passes;
- no provider-native tools, streaming, fallback, retry/backoff, new analysis tools, or financial writes are introduced;
- GitHub-hosted CI passes and integration review finds no blocker.

## Explicit non-goals

- Anthropic, Gemini, Azure OpenAI, Bedrock, or other second provider;
- live-network CI;
- streaming;
- Responses API built-in tools;
- function calling or provider-native tool execution;
- conversation persistence;
- background responses;
- retry/backoff or provider/model fallback;
- secret-manager integration;
- prompt-management infrastructure;
- finance/runtime/tool redesign;
- financial write capability.
