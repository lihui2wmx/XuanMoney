# Canonical Handoff

## Current status

Milestone: **First Real Provider Adapter v0.1 Readiness/Design — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `f3c2cf66917a28a580ea16e4a28ae212de3753d9`

Merged PR: **#20 — `docs: define first real provider adapter readiness`**

Final PR head: `1d09f6c1e94c44d47883868be9c21f8dd781666f`

PR CI #334 passed on GitHub-hosted `ubuntu-latest` / Python 3.12. Integration design review `5102812238` found no remaining architecture, safety, dependency, or bounded-scope blocker.

The project is licensed under **Apache License 2.0**.

## Integrated readiness decision

The first real provider target is **OpenAI Responses API** using the official Python `openai` SDK.

The governing design is `docs/OPENAI_PROVIDER_ADAPTER.md`.

The readiness increment installed no SDK, revealed no live credential, constructed no live client, and sent no provider network request.

## Approved implementation boundary

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

Approved design decisions:

- registry identifier is exactly `openai`;
- implementation dependency target is `openai>=3.7,<4`;
- only application-owned `xuanmoney.providers` code may import the provider SDK;
- `xuanmoney.model`, runtime, finance, tools, and credentials packages remain provider-SDK-free;
- trusted `OpenAIProviderFactory` may reveal `ProtectedSecret` only for SDK client construction;
- SDK client must explicitly use `max_retries=0` so repository `max_attempts = 1` remains true;
- `ProviderConfiguration.request_timeout_seconds` maps to SDK timeout;
- `ProviderConfiguration.model_id` maps directly to the Responses API model parameter;
- one `ModelRequest` maps to at most one synchronous Responses API request;
- initial translation uses instructions/input only and sends no provider-native tools;
- successful canonical text maps to `ModelResponse(content=..., provider="openai")`;
- blank/missing/unusable text fails closed as `INVALID_RESPONSE`;
- raw SDK response objects must not enter `ModelResponse.metadata`;
- provider-specific errors normalize into the existing stable `ProviderFailureCode` taxonomy without raw diagnostics, payloads, headers, credentials, or retained exception chains.

Required deterministic failure coverage:

```text
authentication/credential failure -> AUTHENTICATION_FAILED
timeout                           -> TIMEOUT
rate limit                        -> RATE_LIMITED
service / >=500                   -> SERVICE_UNAVAILABLE
connection / transport            -> TRANSPORT_ERROR
reliably classifiable bad application configuration -> INVALID_CONFIGURATION
missing/unusable response text    -> INVALID_RESPONSE
unexpected SDK exception          -> TRANSPORT_ERROR
```

## Preserved invariants

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
one ModelProvider.complete() call per reached runtime phase
```

No SDK retry, application retry/backoff, provider/model fallback, streaming, background responses, provider-native tools/function calling, autonomous tool loop, new model-callable analysis tool, runtime/finance expansion, or financial write behavior is authorized by this design.

## Verification

- readiness branch base: `main@cc02dfdf620becae109a3db18552e8befcad0e9b`;
- pre-final-sync reviewed head `9207ff77ae69d5aebf516347b21fe0d85ad9e4b1`: PR CI #332 success;
- final readiness head `1d09f6c1e94c44d47883868be9c21f8dd781666f`: PR CI #334 success;
- branch was `behind_by=0` and PR mergeable before merge;
- integration design review `5102812238`: no blocker;
- squash merge commit: `f3c2cf66917a28a580ea16e4a28ae212de3753d9`;
- no production dependency or runtime code was changed by the readiness milestone.

## Current limitations

- the official OpenAI SDK is still not installed;
- no `OpenAIProviderFactory` or OpenAI adapter implementation exists yet;
- no live provider network call or credential test exists;
- no second provider is selected;
- no retry/backoff, fallback, streaming, provider-native tools, secret manager, production API/UI, new analysis tool, or financial write capability exists.

## Recommended next bounded action

**Start `OpenAI Provider Adapter v0.1` on a fresh feature branch.**

The bounded implementation should:

1. add bounded official dependency `openai>=3.7,<4`;
2. implement one trusted `OpenAIProviderFactory` and one `ModelProvider` adapter under `xuanmoney.providers`;
3. construct the SDK client with configured timeout and `max_retries=0`;
4. reveal `ProtectedSecret` only at trusted client construction;
5. translate one `ModelRequest` into at most one synchronous Responses API request and one text response back into `ModelResponse`;
6. normalize provider exceptions into existing stable safe failure codes without raw diagnostics or retained cause/context chains;
7. use deterministic fake/monkeypatched SDK clients for request/response, failure, secret-safety, no-retry, registry/composer, bridge, and runtime tests;
8. keep live-network integration out of normal CI;
9. preserve all runtime/tool/finance/read-only boundaries.

Do **not** add Anthropic/Gemini/Azure/Bedrock support, live-network CI, retry/backoff, fallback, streaming, provider-native tool calling, new analysis tools, runtime/finance expansion, or financial write behavior.
