# AI Development Workflow

This document defines the repository-native workflow for AI coding agents and human contributors. Chat history is never a required source of truth.

## Source-of-truth order

When instructions or status appear to conflict, resolve them in this order:

1. `AGENTS.md` — repository-wide invariants and safety boundaries;
2. `docs/HANDOFF.md` — current branch, verified state, active bounded increment, and next action;
3. `docs/ARCHITECTURE.md` — stable module and trust boundaries;
4. `docs/DEVELOPMENT_LOG.md` — chronological milestone record;
5. tests and implementation;
6. `README.md` — public project overview.

If documentation and code disagree, do not silently choose one. Verify the behavior with tests and update the stale source in the same bounded change.

## Session startup protocol

Before changing code, an AI agent should:

1. read `AGENTS.md`;
2. read `docs/HANDOFF.md`;
3. read the relevant architecture and development-log sections;
4. inspect the current branch, HEAD, recent commits, and working tree when a local checkout is available;
5. inspect the implementation and tests touched by the active increment;
6. run the existing test suite before broad changes when practical;
7. state the smallest implementation boundary that advances the active increment.

Do not infer project state from a previous conversation when the repository can answer it.

## Bounded-increment protocol

Each increment should have one primary capability or invariant. The default sequence is:

```text
inspect -> define boundary -> implement deterministic core -> add tests
        -> run validation -> update handoff/log -> commit
```

Rules:

- keep financial formulas and accounting rules out of prompts;
- fail closed on ambiguous financial semantics;
- preserve provenance/evidence through every deterministic transformation;
- do not combine unrelated refactors with a feature increment;
- do not introduce financial write actions during the read-only v0.1 milestone;
- prefer typed contracts and explicit state transitions;
- add a dependency only when the active increment requires it;
- record intentional architecture changes in documentation in the same increment.

## Verification protocol

Minimum local verification for Python changes:

```bash
python -m pip install -e ".[dev]"
pytest
```

CI is the integration authority for repository changes. Core CI must use GitHub-hosted runners, currently `ubuntu-latest`. Do not use `self-hosted` runners. Prefer GitHub-maintained actions for core checkout/runtime setup.

A failing test or CI run is part of the active work. Diagnose it before declaring the increment complete.

## Handoff protocol

Before ending a meaningful development session, update `docs/HANDOFF.md` so a fresh agent can resume without conversation context. It must contain:

- current milestone and status;
- development branch and verified HEAD when known;
- implemented capabilities;
- tests/CI actually run and their result;
- current trust/safety boundary;
- unresolved issues or known limitations;
- exactly one recommended next bounded increment;
- explicit non-goals for that next increment.

Update `docs/DEVELOPMENT_LOG.md` for milestone-level changes, but keep `HANDOFF.md` concise and current rather than chronological.

## Git and integration workflow

- `main` is the stable integration branch.
- Development happens on focused branches such as `feat/...`, `fix/...`, or `docs/...`.
- Use Conventional Commit-style subjects where practical.
- Do not force-push shared work unless recovery requires it and the reason is documented.
- Do not merge a milestone merely because code exists; satisfy its exit conditions and CI first.
- Pull requests should describe the bounded change, trust-boundary impact, validation evidence, and follow-up boundary.

## Decision discipline

An AI agent may make ordinary implementation choices inside the active boundary. It should not silently change:

- accounting semantics;
- security or permission policy;
- the read-only/write boundary;
- public data contracts;
- milestone exit conditions.

Such changes require an explicit repository-visible rationale before implementation.
