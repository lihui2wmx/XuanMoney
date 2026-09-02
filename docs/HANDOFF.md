# Canonical Handoff

## Current status

Milestone: **ModelPort Provider Bridge v0.1**

Status: **READY FOR INTEGRATION — review blockers resolved; final docs-synchronized CI pending**

Development branch: `feat/model-port-provider-bridge-v0.1`

Integration PR: **#8 — `feat: add model port provider bridge v0.1`**

Base: `main` at `260c00a98007d4a58b59ce0261e1b017d39b6664`, which contains Model Provider Contract v0.1 plus its post-merge handoff synchronization.

The project is licensed under **Apache License 2.0**.

## Implemented bridge

The branch closes the gap between the runtime-facing `ModelPort` and lower-level `ModelProvider` transport contract:

```text
BoundedModelRuntime
        -> ModelPort
        -> ModelPortProviderBridge   # xuanmoney.runtime
        -> ModelProvider             # xuanmoney.model transport
        -> Provider Adapter
        -> external model service (future)
```

`ModelPortProviderBridge` implements:

```text
plan(PlanningRequest) -> object
synthesize(SynthesisRequest) -> object
```

For each reached model phase, the bridge:

1. receives the typed runtime request;
2. creates exactly one typed `ModelRequest` with an explicit `planning` or `synthesis` phase;
3. includes the serialized runtime request and expected response JSON Schema in transport context;
4. calls the injected `ModelProvider.complete()` exactly once;
5. strictly JSON-decodes `ModelResponse.content`;
6. returns the decoded value as an untrusted object to `BoundedModelRuntime`.

Strict JSON decoding rejects malformed JSON and non-standard numeric constants (`NaN`, `Infinity`, `-Infinity`). The bridge deliberately does not validate `PlannerDecision` or `SynthesisOutput`; those checks remain runtime-owned.

## Package dependency boundary

The first integration review found one blocker: the initial bridge location under `xuanmoney.model` inverted the intended dependency direction by making the lower-level provider transport package depend on runtime contracts.

That blocker is corrected:

- `ModelPortProviderBridge` lives in `xuanmoney.runtime.provider_bridge`;
- `xuanmoney.runtime` exports the bridge;
- `xuanmoney.model` exports only provider transport contracts and remains independent of `xuanmoney.runtime`;
- dependency direction is `runtime bridge -> model provider transport`, never the reverse;
- response JSON Schemas are copied into each transport request so provider-side mutation cannot alter cached schemas for later calls.

## Preserved runtime boundary

The execution invariant remains:

```text
single plan -> at most one registered tool -> single synthesis -> terminal
```

`BoundedModelRuntime` still owns:

- planner decision validation;
- controlled tool registry enforcement;
- tool request/response validation;
- synthesis output validation;
- terminal failure classification;
- provider exception sanitization.

The bridge must not:

- invoke financial tools directly;
- add hidden tools or hidden retries;
- select an alternate provider or tool after failure;
- invoke SQL, Python, shell, filesystem, or dynamic imports;
- alter financial formulas, semantic mappings, validators, or permissions;
- perform financial write operations;
- introduce an autonomous ReAct loop.

## Verification

Canonical command:

```bash
python -m pip install -e ".[dev]"
pytest
```

Verified anchors:

- `43b14f3a43bac781d83a984cccc916349a080e6d`: initial implementation/bridge tests, push CI #141 **success**;
- `454ab43373592b034a8f441016009a551f5c1bbe`: initial documentation synchronization, push CI #148 **success**;
- `12e20c70f9b495c6837ed9f98d3d975d8e3b06b6`: package-layering correction, PR CI #167 **success**;
- `be90517c18594a4805bf506b4ce7b81cc2a538ae`: review-state synchronization, PR CI #171 **success**;
- `865f753faf817a83e2a0dcd6b750396ead337583`: strict JSON transport hardening, PR CI #175 **success**.

The deterministic bridge tests cover:

- planning transport translation;
- synthesis transport translation;
- full `BoundedModelRuntime` completion through a fake provider;
- runtime-owned `invalid_plan` validation after bridge decoding;
- malformed provider JSON -> terminal planner exception without retry;
- non-standard JSON numeric constants -> terminal planner exception without retry;
- provider exception sanitization through the runtime boundary;
- malformed synthesis JSON -> terminal synthesis exception without retry;
- exactly one provider call per reached phase.

This final provider-contract/development-log/handoff synchronization follows the green strict-JSON anchor and triggers fresh current-head checks. Merge remains gated on those checks.

## Scope exclusions

This milestone contains no:

- real OpenAI/Anthropic/Gemini or other provider SDK;
- provider credentials or secret handling;
- external model network call;
- streaming;
- provider-specific function calling;
- provider fallback or retry policy;
- new model-callable tools;
- Finance Kernel or Tool Registry change;
- filesystem/SQL/Python/shell execution expansion;
- financial write path.

## Known limitations

- `ModelProvider` still has only deterministic local test implementations;
- provider credential/configuration policy is not defined;
- provider network timeout/rate-limit policy is not defined;
- provider observability/redaction policy is not defined;
- no production API/UI exists.

## Recommended next bounded action

**Verify final current-head PR #8 CI and perform final integration review only.**

If the final current-head checks are green, the branch remains ahead of and not behind `main`, review threads contain no blocker, and the changed-file set contains no execution-surface expansion, PR #8 is eligible for squash integration.

Do not add a real provider adapter to PR #8.
