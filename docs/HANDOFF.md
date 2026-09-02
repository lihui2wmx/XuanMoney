# Canonical Handoff

## Current status

Milestone: **Post-Runtime integration checkpoint**

Status: **Bounded Model Runtime v0.1 merged; provider-adapter work not started**

Current maintenance branch: `chore/post-runtime-handoff`

`main` includes **Bounded Model Runtime v0.1** squash-merged through PR #5 at:

```text
d3fb61a789e70f2e4029605462a294543e6fdc39
```

The project is licensed under **Apache License 2.0**.

## Merged capability boundary

The merged runtime enforces:

```text
user query
  -> ModelPort.plan() exactly once
  -> typed PlannerDecision
  -> at most one AnalysisToolRegistry invocation
  -> validated structured tool result
  -> ModelPort.synthesize() exactly once
  -> validated final answer
```

There is no autonomous retry loop and no ReAct-style continuation.

Current model-callable tools remain:

```text
analyze_financials
analyze_dimension
```

Provider/model code must not bypass the controlled registry, create hidden tools, invoke unrestricted SQL/Python/shell/filesystem paths, alter finance formulas or validators, or perform financial write actions.

## Verification state

PR #5 current head before integration was:

```text
c8c45c0c2e51684bfa97f3a86583ab4b3fc77b4f
```

Its PR-triggered GitHub Actions CI completed successfully on the official GitHub-hosted `ubuntu-latest` runner. There were no submitted reviews or unresolved review threads, and PR #5 was squash-merged with expected-head protection.

Canonical local validation remains:

```bash
python -m pip install -e ".[dev]"
pytest
```

## Known limitations

- no external LLM/provider adapter exists;
- no provider authentication/configuration exists;
- no API/UI exists;
- the financial statement model remains intentionally simplified;
- dimensional analysis remains one dimension at a time;
- no FX conversion policy exists;
- application filesystem ingestion is not model-callable;
- no unrestricted SQL/Python execution exists;
- no financial write tools exist.

## Recommended next bounded action

Create a fresh branch from current `main` for **Model Provider Adapter v0.1** and define only the minimal provider-neutral adapter contract around the existing `ModelPort`.

The first provider-adapter increment should be contract-only:

- provider identity/configuration types;
- translation boundary between provider payloads and `PlanningRequest` / `SynthesisRequest`;
- stable provider error normalization contract;
- deterministic fake-adapter tests.

Do **not** connect a real external API, add secrets, add retry policy, change runtime execution policy, or introduce new tools in the same increment.
