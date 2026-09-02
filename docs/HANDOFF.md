# Canonical Handoff

## Current status

Milestone: **Model Provider Contract v0.1**

Status: **CONTRACT IMPLEMENTATION COMPLETE — awaiting integration review**

Development branch: `feat/model-provider-contract-v0.1`

Base: latest stable main after Bounded Model Runtime and Controlled Analysis Tools integration.

The project is licensed under **Apache License 2.0**.

## Implemented boundary

The branch adds the provider-neutral model boundary above the bounded runtime:

```text
BoundedModelRuntime
        -> ModelProvider contract
        -> Provider adapter boundary
        -> external model implementation (future)
```

Implemented:

- typed model request/response schemas;
- provider-neutral protocol;
- adapter boundary;
- deterministic fake adapter for tests;
- runtime/provider integration tests;
- provider contract documentation.

## Current restrictions

No external model provider exists yet.

Provider implementations must not:

- bypass BoundedModelRuntime;
- call financial tools directly;
- execute SQL, Python, shell, or filesystem operations;
- alter financial formulas or validators;
- create hidden tools;
- perform financial write operations.

The provider layer only translates model input/output. Runtime owns execution policy.

## Verification

Required local verification:

```bash
python -m pip install -e ".[dev]"
pytest
```

CI policy remains:

- GitHub-hosted official runners only;
- `ubuntu-latest`;
- no `self-hosted` runners.

## Integration state

Current branch contains the Model Provider Contract v0.1 increment.

Next action:

1. run current-head CI;
2. open integration PR;
3. merge after review gate.

Do not add a real model SDK in the same integration PR.

## Recommended next bounded action

Create the Model Provider Contract v0.1 integration PR after CI verification.
