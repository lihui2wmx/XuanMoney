# Canonical Handoff

## Current status

Milestone: **ModelPort Provider Bridge v0.1**

Status: **READY FOR SECOND INTEGRATION REVIEW — first review blocker corrected; final current-head CI pending**

Development branch: `feat/model-port-provider-bridge-v0.1`

Integration PR: **#8 — `feat: add model port provider bridge v0.1`**

Base: `main` at `260c00a98007d4a58b59ce0261e1b017d39b6664`, which contains Model Provider Contract v0.1 plus its post-merge handoff synchronization.

The project is licensed under **Apache License 2.0**.

## Implemented bridge

The branch closes the previously explicit gap between the runtime-facing `ModelPort` and lower-level `ModelProvider` transport contract:

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
5. JSON-decodes `ModelResponse.content`;
6. returns the decoded value as an untrusted object to `BoundedModelRuntime`.

The bridge deliberately does not validate `PlannerDecision` or `SynthesisOutput`. Those checks remain runtime-owned.

## Package dependency boundary

The first integration review found one blocker: the initial bridge location under `xuanmoney.model` inverted the intended dependency direction by making the lower-level provider transport package depend on runtime contracts.

That blocker is corrected:

- `ModelPortProviderBridge` now lives in `xuanmoney.runtime.provider_bridge`;
- `xuanmoney.runtime` exports the bridge;
- `xuanmoney.model` exports only `ModelProvider`, `ModelRequest`, and `ModelResponse` and remains transport-only;
- architecture rules explicitly require `runtime bridge -> model provider transport`, never the reverse;
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
- `454ab43373592b034a8f441016009a551f5c1bbe`: initial documentation-synchronized pre-PR head, push CI #148 **success**;
- `12e20c70f9b495c6837ed9f98d3d975d8e3b06b6`: package-layering correction, PR CI #167 **success**.

The bridge test slice covers:

- planning transport translation;
- synthesis transport translation;
- full `BoundedModelRuntime` completion through a deterministic fake provider;
- runtime-owned `invalid_plan` validation after bridge decoding;
- malformed provider JSON -> terminal planner exception without retry;
- provider exception sanitization through the runtime boundary;
- malformed synthesis JSON -> terminal synthesis exception without retry;
- exactly one provider call per reached phase.

This final review-state development-log/handoff synchronization follows the corrected green anchor and triggers fresh current-head checks.

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

**Verify current-head PR #8 CI and perform the second integration review only.**

The second review should confirm that the package dependency direction is corrected, runtime validation/execution policy remains in `BoundedModelRuntime`, provider calls are one-per-phase without retry, and no real provider SDK or execution-surface expansion entered the branch.

If current-head CI is green and the second review finds no blocker, PR #8 is eligible for squash integration. Do not add a real provider adapter to PR #8.
