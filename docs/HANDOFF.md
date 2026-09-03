# Canonical Handoff

## Current status

Milestone: **First Real Provider Adapter v0.1 Readiness/Design**

Status: **ACTIVE — OpenAI target selected and implementation boundary defined**

Development branch: `docs/first-real-provider-adapter-readiness`

Base: `main@cc02dfdf620becae109a3db18552e8befcad0e9b`.

Previous integrated milestone: **Controlled Provider Factory Registry v0.1 — COMPLETE**, merged via PR #18 at `73f7cbb5ffeeeaa79204d5c38f12e2e1c47f6b56` and post-merge synchronized at `cc02dfdf620becae109a3db18552e8befcad0e9b`.

The project is licensed under **Apache License 2.0**.

## Readiness decision

The first real provider target is **OpenAI Responses API** using the official Python `openai` SDK.

The governing design is `docs/OPENAI_PROVIDER_ADAPTER.md`.

This increment is documentation/design only. It does not install the SDK, reveal a live credential, construct a live provider client, or send a provider network request.

## Planned provider boundary

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
        v
Responses API request
        |
        v
ModelResponse
        |
        v
ModelPortProviderBridge
        |
        v
BoundedModelRuntime
```

## Design decisions

- registry identifier is exactly `openai`;
- implementation dependency target is `openai>=3.7,<4`;
- only application-owned `xuanmoney.providers` code may import the provider SDK;
- `xuanmoney.model`, runtime, finance, tools, and credentials packages remain provider-SDK-free;
- trusted `OpenAIProviderFactory` may reveal `ProtectedSecret` only to construct the SDK client;
- SDK client construction must explicitly set `max_retries=0` so repository `max_attempts = 1` remains true;
- `ProviderConfiguration.request_timeout_seconds` maps to the SDK timeout;
- `ProviderConfiguration.model_id` maps directly to the Responses API model parameter;
- one `ModelRequest` maps to at most one synchronous Responses API request;
- initial request translation uses instructions/input only; no provider-native tool surface is enabled;
- successful canonical text output maps to `ModelResponse(content=..., provider="openai")`;
- blank/missing/unusable text fails closed as `INVALID_RESPONSE`;
- raw SDK response objects must not enter `ModelResponse.metadata`;
- provider-specific failures normalize into the existing stable `ProviderFailureCode` taxonomy without raw diagnostics, response bodies, request payloads, headers, credentials, cause chains, or context chains.

Required failure classes to cover deterministically:

```text
authentication/credential failure -> AUTHENTICATION_FAILED
timeout                           -> TIMEOUT
rate limit                        -> RATE_LIMITED
service / >=500                   -> SERVICE_UNAVAILABLE
connection / transport            -> TRANSPORT_ERROR
bad application-owned configuration where reliably classifiable -> INVALID_CONFIGURATION
missing/unusable response text    -> INVALID_RESPONSE
unexpected SDK exception          -> TRANSPORT_ERROR
```

## Preserved invariants

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
one ModelProvider.complete() call per reached runtime phase
```

The implementation milestone must not introduce SDK retries, application retry/backoff, provider/model fallback, streaming, background responses, provider-native tools/function calling, autonomous tool loops, filesystem/SQL/Python/shell access, new model-callable analysis tools, runtime/finance expansion, or financial writes.

## Deterministic implementation test plan

The next implementation milestone should use fake/monkeypatched SDK clients before any live integration and prove:

1. `provider_id="openai"` selects only the OpenAI factory;
2. credential reveal occurs only at trusted client construction;
3. client construction receives configured timeout and `max_retries=0`;
4. model ID, instructions, and input are translated exactly once;
5. successful text maps to a valid `ModelResponse`;
6. authentication, timeout, rate-limit, service, invalid-response, configuration, and generic transport failures normalize to stable safe codes;
7. secret material and raw provider diagnostics remain absent from repr, transport serialization, runtime results, and public failures;
8. deterministic execution works through `ModelPortProviderBridge` and `BoundedModelRuntime`;
9. provider failure causes no retry or second provider call;
10. no provider-native tool configuration is sent.

## Current limitations

- the official OpenAI SDK is not yet installed;
- no `OpenAIProviderFactory` or OpenAI adapter implementation exists yet;
- no live provider network call or credential test exists;
- no second provider is selected;
- no retry/backoff, fallback, streaming, provider-native tools, secret manager, production API/UI, new analysis tool, or financial write capability exists.

## Recommended next bounded action

**After this readiness/design PR passes CI and review, integrate it; then start `OpenAI Provider Adapter v0.1` on a fresh feature branch.**

The implementation increment should add only:

1. bounded official `openai` SDK dependency;
2. one trusted `OpenAIProviderFactory` and one `ModelProvider` adapter;
3. deterministic fake-SDK tests covering request/response and failure mapping;
4. registry/composer/bridge/runtime integration coverage;
5. milestone documentation/handoff synchronization.

Do **not** add Anthropic/Gemini/Azure/Bedrock support, live-network CI, retry/backoff, fallback, streaming, provider-native tool calling, new analysis tools, runtime/finance expansion, or financial write behavior.
