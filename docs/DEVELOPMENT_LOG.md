# Development Log

## 2026-09-02 — Project bootstrap

Status: **COMPLETE**

Established the repository baseline and the first deterministic, read-only finance-analysis slice:

- typed income statement and balance sheet contracts using `Decimal`;
- evidence-bearing metric/finding models;
- profitability metrics and period variance;
- balance-sheet accounting identity validation;
- bounded agent state and service workflow;
- core unit tests and GitHub Actions CI.

## 2026-09-02 — Normalized tabular ingestion and AI handoff workflow

Status: **COMPLETE**

Added explicit semantic aliases, fail-closed CSV/XLSX ingestion, deterministic decimal parsing, provenance, repository-native AI handoff, contribution guidance, and hardened GitHub-hosted CI.

## 2026-09-02 — Profit Bridge v0.1

Status: **COMPLETE — merged via PR #1**

Added deterministic net-profit change decomposition with exact `Decimal` reconciliation, validation, provenance, and service-level tests. PR #1 also established Apache License 2.0 licensing and was squash-merged to `main` at `d65aeda6f0e22319768d0a8213f8c73fd7436eec`.

## 2026-09-02 — Dimensional Analysis v0.1

Status: **COMPLETE — merged via PR #3**

Added explicit one-dimensional ingestion, deterministic member aggregation, member revenue/COGS/gross-profit/gross-margin metrics, new/disappearing member comparison, exact contribution reconciliation, provenance, mixed-currency fail-closed behavior, and `analyze_dimension`. PR #3 was squash-merged to `main` at `6e7334c3fbd576c7f6657ca8f5b70a6a0ceb193c` after successful GitHub-hosted CI.

## 2026-09-02 — Controlled Analysis Tools v0.1

Status: **COMPLETE — merged via PR #4**

Implemented the fixed read-only model-callable boundary:

- immutable `AnalysisToolRegistry` without a public dynamic `register()` API;
- model-callable tools limited to `analyze_financials` and `analyze_dimension`;
- enforced `ToolRisk.READ_ONLY`;
- Pydantic request/response contracts and JSON Schema metadata;
- `extra="forbid"` request envelopes;
- stable tool failures for unknown tool, invalid request, execution failure, and invalid response;
- raw request input omitted from structured validation errors;
- service/domain failures normalized through `ToolInvocationError` / `ToolFailure`;
- filesystem loaders, SQL, Python/shell execution, dynamic imports, and financial writes excluded from the model-callable surface;
- `docs/TOOLS.md` documenting the trust boundary.

Final push and PR checks passed on GitHub-hosted `ubuntu-latest`. PR #4 was squash-merged to `main` at `9934248ade818b66ff14f385ee8063f0791ce837`.

## 2026-09-02 — Bounded Model Runtime v0.1

Status: **COMPLETE — merged via PR #5**

Implemented:

- provider-independent `ModelPort` with separate `plan` and `synthesize` methods;
- typed `PlanningRequest`, `PlannerDecision`, `ToolCallPlan`, `NoToolPlan`, `SynthesisRequest`, and `SynthesisOutput` contracts;
- `BoundedModelRuntime` enforcing one plan, at most one registered tool invocation, and one synthesis;
- fail-closed unknown-tool behavior through the existing controlled registry;
- terminal behavior for invalid arguments, tool execution failure, planner failure, and synthesis failure;
- no retry loop, ReAct loop, SQL/Python fallback, filesystem fallback, or alternate execution path;
- provider exception normalization that does not expose provider exception text in runtime results;
- whitespace-only planner reasons and synthesis answers rejected;
- deterministic fake-model tests for successful flow and major failure paths;
- `docs/RUNTIME.md` defining the runtime/model trust boundary.

PR #5 passed GitHub-hosted CI and was squash-merged to `main` at `d3fb61a789e70f2e4029605462a294543e6fdc39`.

### Runtime invariant

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

No external LLM/provider SDK was added.

## 2026-09-02 — Model Provider Contract v0.1

Status: **COMPLETE — merged via PR #6**

Implemented:

- typed `ModelRequest` and `ModelResponse` contracts with `extra="forbid"`;
- provider-neutral `ModelProvider.complete(ModelRequest) -> ModelResponse` protocol;
- `BaseModelAdapter` provider implementation boundary;
- deterministic `EchoModelAdapter` used only for tests;
- contract tests for typed request/response behavior and forbidden extra fields;
- explicit separation between the runtime-facing `ModelPort` and lower-level `ModelProvider` transport contract;
- provider-boundary documentation;
- no vendor SDK, credentials, external network call, streaming, function calling, financial tool access, or financial write path.

Final PR head `6e204f11fee6a887580b9b4b06d2538831c6bbe8` passed GitHub-hosted PR CI #130. PR #6 was squash-merged to `main` at `c8f18f93b72cd0f4462e0f94a2cbbaebcdafa305`.

## 2026-09-02 — ModelPort Provider Bridge v0.1

Status: **COMPLETE — merged via PR #8**

Implemented:

- runtime-owned `ModelPortProviderBridge` implementing `ModelPort.plan()` and `ModelPort.synthesize()` over an injected lower-level `ModelProvider`;
- provider-neutral phase translation for typed `PlanningRequest` and `SynthesisRequest` values;
- copied response JSON Schema included in each transport request;
- exactly one `ModelProvider.complete()` call for each reached phase;
- strict JSON decoding of `ModelResponse.content`, including rejection of malformed JSON and non-standard `NaN`/`Infinity` constants;
- planner/synthesis semantic validation remains in `BoundedModelRuntime`;
- complete `BoundedModelRuntime` execution through a deterministic fake provider;
- terminal no-retry behavior for malformed transport data and provider exceptions;
- provider exception diagnostics remain sanitized by the existing runtime boundary;
- package dependency direction enforced as `xuanmoney.runtime -> xuanmoney.model`, never the reverse;
- no changes to Finance Kernel, controlled Tool Registry, runtime execution sequence, or financial write boundary.

Integration review found and corrected the initial package-layering inversion before merge. The corrected bridge lives in `xuanmoney.runtime.provider_bridge`, while `xuanmoney.model` remains transport-only.

Final branch head `427b9083b206fa8abb7b97d9cb1f3b558c957f2d` passed PR CI #181. Final integration review found no remaining blocker, and PR #8 was squash-merged to `main` at `b6614b7f207fe6d594c8472758a053c85668bae6`.

### Preserved boundary

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge
        -> ModelProvider
        -> provider adapter (future)
```

No real provider SDK, credential handling, external model network call, hidden retry, new tool, filesystem/SQL/Python/shell path, or financial write capability was introduced.

## 2026-09-03 — Provider Configuration & Safety Contract v0.1

Status: **COMPLETE — merged via PR #10**

Implemented:

- immutable provider-neutral `ProviderConfiguration` with non-blank provider/model identifiers;
- bounded integer request timeout of 1–120 seconds;
- `max_attempts` fixed to exactly `1` and protected against post-validation mutation;
- immutable `CredentialReference` carrying only a source and reference identifier, never a credential value;
- current credential source limited to an environment-variable reference name without reading the environment;
- `extra="forbid"` rejection of unknown and attempted secret/API-key fields;
- stable provider transport failure taxonomy covering configuration, credential availability, authentication, timeout, rate limit, service availability, invalid response, and generic transport failures;
- immutable public `ProviderFailure` whose message is derived only from its stable code, preventing provider-supplied raw diagnostic text;
- `ProviderTransportError` exposing only the sanitized failure contract;
- deterministic tests for valid/invalid configuration, timeout/retry bounds and mutation, environment-reference syntax, secret-field rejection, stable safe messages, failure immutability, and diagnostic/message injection rejection;
- `docs/PROVIDER_SAFETY.md` defining the pre-SDK trust boundary.

Final PR head `93f2d2b8202cb55db31e82efbad11d61f9d78d4c` passed GitHub-hosted PR CI #218 on `ubuntu-latest` / Python 3.12. Final integration review found no remaining architecture or safety blocker, and PR #10 was squash-merged to `main` at `0148962739a80cdb53c25dbbf445dc9584a75a4a`.

No real provider SDK, credential resolver, environment read, network call, retry/backoff, fallback, streaming, logging infrastructure, new model-callable tool, execution-surface expansion, or financial write path was introduced.

## 2026-09-03 — Credential Resolver Boundary v0.1

Status: **COMPLETE — merged via PR #12**

Implemented:

- application-owned `CredentialResolver` protocol accepting the existing non-secret `CredentialReference`;
- runtime-only immutable `ProtectedSecret` with explicit `reveal()` for a future trusted provider integration boundary;
- redacted `str`, `repr`, and formatted output;
- JSON and pickle serialization fail closed rather than expose credential values;
- `ProtectedSecret` rejects empty values;
- stable `CredentialResolutionFailureCode` taxonomy for unsupported source and unavailable credentials;
- sanitized `CredentialResolutionError` that stores no reference identifier, secret value, or raw resolver diagnostic;
- deterministic fake/in-memory resolver tests covering successful resolution, missing references, configuration non-mutation, serialization blocking, redaction, immutability, and diagnostic/reference non-disclosure;
- missing-reference fake resolution avoids retaining a lower-level exception cause/context containing reference material;
- provider transport hardening requiring strict JSON-safe `ModelRequest.context` and `ModelResponse.metadata`;
- arbitrary Python objects including `ProtectedSecret` and non-standard `NaN`/`Infinity` values rejected before provider transport;
- invalid transport inputs hidden from Pydantic validation-error strings;
- mutable transport dict defaults replaced with `Field(default_factory=dict)`;
- package direction preserved as `xuanmoney.credentials -> xuanmoney.model`, never the reverse;
- `docs/CREDENTIALS.md` and `docs/PROVIDER_CONTRACT.md` updated for the integrated safety boundary.

Pre-hardening head `0ebfee86048a09f1af5d9ab490624c87dd491eba` passed PR CI #237. Final head `3640269d2e47551c77bce97e9b8fbccfd4714d54` passed PR CI #248 on GitHub-hosted `ubuntu-latest` / Python 3.12. Integration review `5096676763` found no remaining architecture or safety blocker, and PR #12 was squash-merged to `main` at `84edd3e90c9c5c2551e5314410bd7eb554cfe75e`.

No real environment-variable read, secret manager, provider SDK, network call, retry/backoff, fallback, streaming, logging infrastructure, new model-callable tool, execution-surface expansion, or financial write path was introduced.

## 2026-09-03 — Environment Credential Resolver v0.1

Status: **COMPLETE — merged via PR #14**

Implemented:

- concrete application-owned `EnvironmentCredentialResolver` implementing the existing `CredentialResolver` protocol;
- injected `Mapping[str, str]` input rather than implicit process-environment access;
- present non-empty environment references return `ProtectedSecret` only;
- missing, empty, non-string, and backing-mapping lookup failures normalize to the existing `credential_unavailable` failure;
- unsupported sources normalize to `unsupported_source`;
- lookup failures are normalized outside the backing exception handler so sanitized failures retain no raw diagnostic cause/context chain;
- resolver representation is redacted and does not expose the backing mapping or values;
- deterministic tests use injected mappings/`MappingProxyType` and cover present, missing, empty, non-string, unsupported, and failing-mapping cases;
- existing `ProtectedSecret`, JSON-safe model transport, package direction, `max_attempts = 1`, runtime execution sequence, finance logic, and tool registry remain unchanged.

Implementation head `fd26abe156678faac91e01f2efdeabbe43ee0222` passed PR CI #267. Final head `7646a1d38e105aeb844bba01a96dc0395988273d` passed PR CI #269 on GitHub-hosted `ubuntu-latest` / Python 3.12. Integration review `5096782358` found no remaining architecture or safety blocker, and PR #14 was squash-merged to `main` at `67c957eb199efc8ee8b7c8955635e667237b58f7`.

No provider SDK, provider network call, retry/backoff, fallback, streaming, secret manager, API-key persistence, model/runtime direct environment access, new model-callable tool, or financial write path was introduced.

## 2026-09-03 — Provider Adapter Credential Injection v0.1

Status: **COMPLETE — merged via PR #16**

Implemented:

- application-owned `xuanmoney.providers` composition package;
- `ProviderAdapterFactory` protocol as the trusted provider/client-construction boundary;
- `ProviderAdapterComposer` combining existing `ProviderConfiguration`, `CredentialResolver`, and factory contracts;
- optional credential references resolve once to `ProtectedSecret` before adapter construction;
- generic composer never calls `ProtectedSecret.reveal()`;
- explicit reveal is confined to trusted factory/client construction and raw credential values are not persisted by the generic composition layer;
- unavailable credentials normalize to `ProviderFailureCode.CREDENTIAL_UNAVAILABLE` before factory invocation;
- unsupported credential sources normalize to `ProviderFailureCode.INVALID_CONFIGURATION`;
- unexpected resolver failures and invalid resolver return types fail closed;
- factory/client-construction failures normalize to `ProviderFailureCode.TRANSPORT_ERROR` without retaining raw secret-bearing cause/context chains;
- invalid factory results lacking a callable `complete()` surface fail closed at composition time;
- deterministic integration tests drive a credential-consuming fake provider through `ModelPortProviderBridge` and `BoundedModelRuntime`;
- tests assert fake secret material is absent from model transport request serialization, runtime result serialization, public failures, and composer/factory/adapter representations;
- package direction is `xuanmoney.providers -> xuanmoney.credentials -> xuanmoney.model` plus `xuanmoney.providers -> xuanmoney.model`, with no reverse dependency;
- `docs/PROVIDER_COMPOSITION.md` defines the trusted reveal and failure-normalization boundary.

Verification:

- `707523b7744d9fbba47f70fb8e3365c4a331bcb8`: PR CI #284 success;
- `8b357c947c80eb44adaf2d091f27f3d35aa717fd`: PR CI #294 success after invalid-provider-result hardening;
- final head `9c1e5dbc47931c5cc0720811a3c5799e7a575fca`: PR CI #298 success on GitHub-hosted `ubuntu-latest` / Python 3.12;
- final branch was `behind_by=0`, mergeable, and had no unresolved review threads;
- integration review `5096853542` found no remaining architecture or safety blocker;
- PR #16 was squash-merged to `main` at `572ac05873ba3ff3cebd182fc72d07bb2f2dec65`.

No vendor SDK, provider network call, provider-specific HTTP/auth implementation, retry/backoff, fallback, streaming, secret manager, credential persistence, new model-callable tool, runtime/finance/tool expansion, or financial write path was introduced.

### Next boundary

Start **Controlled Provider Factory Registry v0.1** as a separate bounded increment. Add an immutable application-owned allowlist from validated `provider_id` values to trusted `ProviderAdapterFactory` implementations, fail closed on unknown or duplicate identifiers, and prohibit dynamic imports, public registration, plugin discovery, model-controlled provider selection, retry/fallback, vendor SDKs, and network calls in that milestone.

## 2026-09-03 — Controlled Provider Factory Registry v0.1

Status: **COMPLETE — merged via PR #18**

Implemented:

- immutable snapshot-based application-owned `ProviderFactoryRegistry`;
- explicit fixed `provider_id -> ProviderAdapterFactory` allowlist;
- whitespace-normalized non-blank provider identifiers aligned with `ProviderConfiguration` semantics;
- duplicate/ambiguous identifiers fail closed during registry construction;
- invalid factories without callable `build()` fail closed before credential resolution;
- unknown configured providers normalize to sanitized `ProviderFailureCode.INVALID_CONFIGURATION` before factory invocation;
- provider construction delegates through the existing `ProviderAdapterComposer` and credential-resolution boundary;
- no public `register()`, dynamic import, entry-point/plugin/filesystem discovery, model-controlled provider loading, fallback, or retry-based switching;
- deterministic registry-level credential-consuming fake factory integration executes through `EnvironmentCredentialResolver`, trusted reveal/construction, `ModelPortProviderBridge`, and `BoundedModelRuntime`;
- test secret material is asserted absent from registry/factory/provider representations, provider request serialization, and runtime result serialization;
- `docs/PROVIDER_REGISTRY.md` documents the provider-selection trust boundary.

Verification:

- core implementation/test head `2300791fa062d66203791fc82906973b6a22106c`: PR CI #308 success;
- handoff synchronization head `df23f502e860d10b07ba89c471b29c474cc4da75`: PR CI #310 success;
- reviewed pre-final-sync head `9322313082cdff06f85a7ad76d8c40310672c0ce`: PR CI #316 success;
- final handoff head `1f81f1e2b2ca76ab5527f73250855358c5c66625`: PR CI #318 success;
- final feature head `4cc6d621c9296cff5424ae13f95b0607a20cb931`: PR CI #320 success;
- branch was `behind_by=0`, PR was mergeable, and no review threads remained unresolved;
- integration review `5096980951` found no remaining architecture, safety, or bounded-scope blocker;
- PR #18 was squash-merged to `main` at `73f7cbb5ffeeeaa79204d5c38f12e2e1c47f6b56`.

No vendor SDK, external provider network call, provider-specific HTTP/auth implementation, retry/backoff, fallback, streaming, secret-manager integration, dynamic provider discovery, new model-callable tool, runtime/finance/tool expansion, or financial write path was introduced.

### Next boundary

Perform a bounded **First Real Provider Adapter v0.1 readiness/design review** before implementation. Select exactly one provider target and define its dependency/client surface, timeout application, authentication construction, request/response translation, stable failure mapping, deterministic test strategy, and preserved no-retry/no-fallback/bounded-runtime constraints before adding real network behavior.

## 2026-09-03 — OpenAI Provider Adapter v0.1

Status: **COMPLETE — merged via PR #22**

Implemented:

- bounded official dependency `openai>=3.7,<4`;
- application-owned `OpenAIProviderFactory` as the only OpenAI-specific trusted `ProtectedSecret.reveal()` boundary;
- application-owned synchronous `OpenAIProviderAdapter` implementing the existing `ModelProvider.complete(ModelRequest) -> ModelResponse` contract;
- SDK client construction applies configured timeout and explicitly sets `max_retries=0`, preserving repository `max_attempts = 1`;
- existing `ModelRequest(prompt, context)` contract is preserved, with `prompt -> Responses instructions` and deterministic JSON-safe `context -> Responses input`;
- one `ModelProvider.complete()` maps to at most one synchronous `responses.create()` call;
- no provider-native tools, streaming, background responses, application retry/backoff, provider/model fallback, or alternate execution path is introduced;
- nonblank canonical `output_text` maps to `ModelResponse(provider="openai")`; missing/blank text fails closed as `INVALID_RESPONSE`;
- authentication/permission, timeout, rate limit, service, bad-request/configuration, connection, and unexpected SDK failures normalize to existing stable safe `ProviderFailureCode` values;
- normalized failures retain no raw provider diagnostic, credential material, exception cause, or exception context;
- deterministic fake-SDK tests cover factory construction, request mapping, no-tools/no-streaming/no-background behavior, failure normalization, invalid configuration/client surfaces, secret non-disclosure, and registry/composer/bridge/runtime integration;
- implementation corrected the readiness-document mismatch that described nonexistent `ModelRequest.instructions/input` fields without changing lower-level model/runtime schemas.

Verification:

- implementation/test head `26d317d1398b717d15d468288db3dab866231c6c`: PR CI #346 success on GitHub-hosted `ubuntu-latest` / Python 3.12;
- documentation-synchronized head `564f8becdb06ffd6ea653e8281d5e8035707ffd8`: PR CI #350 success;
- development-log synchronized head `c21232783ee59bf932a545ca5507823ee234a0ff`: PR CI #352 success;
- final handoff head `318a10e565696cb492bce6d02d4a1c5843fb2bfe`: PR CI #354 success;
- final branch was `behind_by=0`, PR #22 was mergeable, and no review threads remained;
- integration review `5103040205` found no remaining code, architecture, provider-safety, dependency-direction, governance, or bounded-scope blocker;
- PR #22 was squash-merged to `main` at `40ddbf723fda8dad0ba8044286bd2a5c2ed3d072`.

No live provider network call, live credential CI, second provider, retry/backoff, fallback, streaming, background response mode, provider-native tools/function calling, secret-manager integration, runtime/finance/tool expansion, production API/UI, or financial write path is introduced.

### Next boundary

Start **Application Runtime Composition v0.1** as a separate bounded increment. Add one application-owned construction boundary that wires validated provider configuration, injected credential resolution, the fixed provider factory registry, `ModelPortProviderBridge`, the existing controlled analysis tool registry, and `BoundedModelRuntime` together. Keep deterministic tests network-free and preserve all no-retry/no-fallback/read-only/model-control boundaries.
