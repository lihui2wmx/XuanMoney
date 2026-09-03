# OpenAI Provider Adapter v0.1

## Decision

The first real provider target is **OpenAI Responses API** through the official Python `openai` package.

The readiness/design review was integrated before implementation. This document now governs the implementation boundary and records one contract correction discovered during implementation.

## Provider contract correction

The readiness draft described a hypothetical `ModelRequest.instructions/input` shape. The actual repository transport contract is:

```text
ModelRequest(prompt: str, context: dict[str, object])
```

and `ModelPortProviderBridge` already relies on that contract. The OpenAI adapter therefore does **not** change `xuanmoney.model` schemas. The approved mapping is:

```text
ModelRequest.prompt  -> Responses API instructions
ModelRequest.context -> deterministic JSON string -> Responses API input
```

`context` is already required to be strict JSON-safe by `ModelRequest`, so the adapter serializes it deterministically with non-standard JSON numbers disabled upstream. This preserves the existing model/runtime package boundary rather than widening it for one provider.

## Dependency boundary

Implementation dependency:

```text
openai>=3.7,<4
```

Only application-owned `xuanmoney.providers` code may import `openai`. `xuanmoney.model`, `xuanmoney.runtime`, `xuanmoney.finance`, `xuanmoney.tools`, and `xuanmoney.credentials` remain provider-SDK-free.

No separate direct HTTP client dependency is introduced by XuanMoney.

## Provider identifier

The controlled registry identifier is exactly:

```text
openai
```

Selection remains application-owned through `ProviderConfiguration.provider_id`. Model output and model-callable tool arguments never select or alter the provider.

## Trusted construction boundary

`OpenAIProviderFactory` belongs under application-owned `xuanmoney.providers`.

For `provider_id="openai"`, a credential is required. The factory is the only OpenAI-specific component permitted to call `ProtectedSecret.reveal()`.

The raw value is passed directly into official SDK client construction and is not persisted separately by the factory or adapter.

Client construction policy:

```text
OpenAI(
    api_key=<revealed credential>,
    timeout=float(configuration.request_timeout_seconds),
    max_retries=0,
)
```

`max_retries=0` is mandatory because the official SDK otherwise retries selected failures automatically. Repository policy fixes provider attempts to one.

## Request mapping

Each `ModelProvider.complete(ModelRequest)` maps to at most one synchronous `client.responses.create(...)` call.

Current mapping:

```text
ProviderConfiguration.model_id -> model
ModelRequest.prompt             -> instructions
JSON(ModelRequest.context)      -> input
```

The context serialization is deterministic (`sort_keys=True`, compact separators) and remains a transport operation only. The adapter does not reinterpret planning, synthesis, evidence, finance semantics, or response schemas carried inside context.

No provider-native tools are supplied. No web search, file search, computer use, shell, code interpreter, function calling, MCP, or other built-in/custom tool surface is enabled.

No streaming or background response mode is enabled.

## Response mapping

The adapter returns one `ModelResponse`.

For v0.1:

- response text is read from the SDK response's canonical `output_text` surface;
- blank, missing, or unusable text fails closed as `ProviderFailureCode.INVALID_RESPONSE`;
- `ModelResponse.provider` is the stable string `openai`;
- `ModelResponse.metadata` remains empty/minimal and JSON-safe;
- raw SDK response objects are never embedded in metadata.

## Failure normalization

Provider-specific exceptions are translated into the existing stable taxonomy without preserving raw exception text, response bodies, headers, request payloads, API keys, or exception cause/context chains.

Required mapping:

```text
AuthenticationError / PermissionDeniedError -> AUTHENTICATION_FAILED
APITimeoutError                             -> TIMEOUT
RateLimitError                              -> RATE_LIMITED
InternalServerError / >=500                 -> SERVICE_UNAVAILABLE
BadRequestError / NotFoundError / 422       -> INVALID_CONFIGURATION
APIConnectionError                          -> TRANSPORT_ERROR
missing/unusable output_text                -> INVALID_RESPONSE
unexpected SDK/client exception             -> TRANSPORT_ERROR
```

Generic `APIStatusError` values may also be normalized by stable HTTP status class when the dedicated SDK subclass is not observed. Raw provider diagnostics are never used as public failure messages.

All public failures remain `ProviderTransportError` with code-derived safe messages only.

## Runtime invariants

The implementation preserves:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
one ModelProvider.complete() call per reached runtime phase
one Responses API call per complete() invocation
```

The adapter does not add:

- SDK automatic retries;
- application retry/backoff;
- provider or model fallback;
- streaming;
- background responses;
- provider-native autonomous tool loops;
- provider-native function/tool invocation;
- hidden filesystem/SQL/Python/shell access.

## Deterministic test strategy

Normal CI uses no live API key and sends no network request.

`tests/test_openai_provider_adapter.py` uses a deterministic fake SDK client boundary and proves:

1. trusted factory reveals `ProtectedSecret` only for client construction;
2. client construction receives configured timeout and `max_retries=0`;
3. `prompt`, JSON-safe `context`, and model ID map exactly once into one Responses API request;
4. no `tools`, `stream`, or `background` argument is sent;
5. successful `output_text` maps to `ModelResponse(provider="openai")`;
6. blank output fails closed as `INVALID_RESPONSE`;
7. authentication, permission, timeout, rate-limit, service, bad-request/model, not-found, unprocessable, connection, and unexpected failures normalize to stable codes;
8. public failures retain no raw diagnostic or credential material and no cause/context chain;
9. wrong provider IDs, missing credentials, and invalid SDK client surfaces fail closed;
10. controlled registry + injected environment resolver + trusted factory + adapter + `ModelPortProviderBridge` + `BoundedModelRuntime` execute end to end with deterministic responses and no secret disclosure.

A later optional live smoke test must be a separate milestone and must not become normal CI or require repository secrets by default.

## Implementation files

```text
src/xuanmoney/providers/openai_adapter.py
src/xuanmoney/providers/__init__.py
pyproject.toml
tests/test_openai_provider_adapter.py
docs/OPENAI_PROVIDER_ADAPTER.md
docs/HANDOFF.md
docs/DEVELOPMENT_LOG.md
```

Finance kernels, controlled analysis tools, runtime state transitions, model transport schemas, credential resolver semantics, and registry mutation policy remain unchanged.

## Exit conditions for OpenAI Provider Adapter v0.1

The milestone is complete only when:

- official `openai` SDK dependency is bounded;
- one trusted `OpenAIProviderFactory` and one provider adapter implement existing contracts;
- SDK retries are explicitly disabled;
- configured timeout and model ID are applied;
- credential reveal remains confined to trusted client construction;
- one `ModelRequest` produces at most one SDK request;
- existing `prompt/context` transport contract is preserved;
- successful canonical text produces a valid `ModelResponse`;
- stable failure mappings are covered deterministically;
- no raw provider diagnostics/secrets leak through public failures, transport, runtime results, or repr;
- deterministic registry/bridge/runtime integration passes;
- no provider-native tools, streaming, background mode, fallback, retry/backoff, new analysis tools, or financial writes are introduced;
- GitHub-hosted CI passes and integration review finds no blocker.

## Explicit non-goals

- Anthropic, Gemini, Azure OpenAI, Bedrock, or another provider;
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
