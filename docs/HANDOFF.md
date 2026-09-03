# Canonical Handoff

## Current status

Milestone: **OpenAI Provider Adapter v0.1 — COMPLETE**

Status: **INTEGRATED — post-merge handoff synchronization**

Main integration commit: `40ddbf723fda8dad0ba8044286bd2a5c2ed3d072`

Merged PR: **#22 — `feat: add OpenAI provider adapter v0.1`**

Final PR head: `318a10e565696cb492bce6d02d4a1c5843fb2bfe`

Final PR CI #354 passed on GitHub-hosted `ubuntu-latest` / Python 3.12. Integration review `5103040205` found no remaining code, architecture, provider-safety, dependency-direction, governance, or bounded-scope blocker.

The project is licensed under **Apache License 2.0**.

## Integrated provider boundary

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
        +--> deterministic JSON(context) -> Responses input
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

Integrated through PR #22:

- bounded official dependency `openai>=3.7,<4`;
- OpenAI SDK imports remain confined to application-owned `xuanmoney.providers`;
- `OpenAIProviderFactory` is the only OpenAI-specific trusted credential reveal/client-construction boundary;
- SDK client construction applies configured timeout and explicitly sets `max_retries=0`;
- the existing `ModelRequest(prompt, context)` transport contract remains unchanged;
- one `OpenAIProviderAdapter.complete()` issues at most one synchronous Responses API request;
- no provider-native tools, streaming, background execution, retry/backoff, provider/model fallback, or alternate execution path is enabled;
- canonical nonblank `output_text` maps to `ModelResponse(provider="openai")`;
- authentication/permission, timeout, rate-limit, service, configuration, connection, invalid-response, and unexpected SDK failures normalize to existing stable safe failure codes;
- normalized public failures retain no raw provider diagnostics, credential material, cause chain, or context chain;
- deterministic tests cover factory construction, request mapping, failure normalization, secret non-disclosure, controlled registry/composer integration, and execution through `ModelPortProviderBridge` and `BoundedModelRuntime`;
- no live credential or external OpenAI request is used in normal CI.

## Verification

- implementation/test head `26d317d1398b717d15d468288db3dab866231c6c`: PR CI #346 success;
- documentation-synchronized head `564f8becdb06ffd6ea653e8281d5e8035707ffd8`: PR CI #350 success;
- development-log synchronized head `c21232783ee59bf932a545ca5507823ee234a0ff`: PR CI #352 success;
- final handoff head `318a10e565696cb492bce6d02d4a1c5843fb2bfe`: PR CI #354 success;
- final branch was `behind_by=0`, PR #22 was mergeable, and no review threads remained;
- integration review `5103040205`: no blocker;
- squash merge commit: `40ddbf723fda8dad0ba8044286bd2a5c2ed3d072`.

## Preserved invariants

```text
single plan -> at most one registered tool -> single synthesis -> terminal
max_attempts = 1
one ModelProvider.complete() call per reached runtime phase
one Responses API call per complete() invocation
```

The project remains read-only. Provider integration does not authorize new tool surfaces, filesystem/SQL/Python/shell access, provider-native tool execution, or financial writes.

## Current limitations

- no application-owned bootstrap/factory yet assembles provider configuration, credential resolver, fixed provider registry, provider bridge, controlled analysis registry, and bounded runtime into one reusable runtime construction boundary;
- no live OpenAI network smoke test has been executed;
- no live credential is used in normal tests or CI;
- no second provider exists;
- no streaming/background Responses API mode or provider-native tool calling;
- no retry/backoff or provider/model fallback;
- no secret-manager integration;
- no production API/UI;
- no new analysis tool, runtime/finance expansion, or financial write capability.

## Recommended next bounded action

**Start `Application Runtime Composition v0.1` as a separate feature increment.**

The next increment should add one application-owned construction boundary that:

1. accepts validated `ProviderConfiguration` plus an injected credential source mapping/resolver;
2. constructs the fixed provider registry containing the approved `openai -> OpenAIProviderFactory` mapping;
3. builds the selected provider through the existing registry/composer credential boundary;
4. wraps it in `ModelPortProviderBridge`;
5. constructs `BoundedModelRuntime` with the existing controlled analysis tool registry;
6. exposes no model-controlled provider selection, dynamic registration, environment access from lower layers, retry/fallback, provider-native tools, or write path;
7. is tested entirely with deterministic fakes/monkeypatching so normal CI remains network-free and credential-free.

Do **not** add a CLI/API/UI, live-network CI, second provider, retry/backoff, fallback, streaming, provider-native tool calling, new analysis tools, runtime/finance expansion, or financial write behavior in the same increment.
