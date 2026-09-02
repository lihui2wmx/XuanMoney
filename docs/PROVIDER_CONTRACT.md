# Model Provider Contract v0.1

## Scope

This document defines the boundary between XuanMoney runtime orchestration and external model providers.

## Contract

```text
BoundedModelRuntime
        |
        v
ModelProvider
        |
        v
Provider Adapter
        |
        v
External model service
```

The provider layer only translates model input/output. It does not own execution policy.

## Allowed responsibilities

- transform runtime requests into provider-specific requests;
- transform provider responses into typed model responses;
- expose provider metadata.

## Forbidden responsibilities

Provider adapters must not:

- invoke financial tools directly;
- access SQL, filesystem, or shell execution;
- modify financial formulas or validators;
- create hidden tools;
- implement autonomous retry loops;
- perform financial write operations.

## Current state

The repository currently contains provider-neutral contracts and deterministic test adapters only. No external model SDK is part of this layer.
