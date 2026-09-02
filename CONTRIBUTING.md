# Contributing to XuanMoney

XuanMoney is an open-source, evidence-first finance-agent project. Contributions should preserve deterministic financial semantics and auditable provenance.

## Development setup

Requirements: Python 3.12+

```bash
python -m pip install -e ".[dev]"
pytest
```

## Before changing code

Read:

1. `AGENTS.md`;
2. `docs/HANDOFF.md`;
3. `docs/AI_WORKFLOW.md`;
4. the architecture section relevant to your change.

The canonical handoff defines the current bounded increment and known limitations.

## Branches

Do not develop directly on `main`. Use focused branches such as:

- `feat/<capability>`
- `fix/<problem>`
- `docs/<topic>`

## Financial correctness rules

- Use `Decimal` for monetary calculations.
- Put deterministic formulas and accounting rules in the finance/domain layers, not prompts.
- Preserve evidence/provenance for material calculated results.
- Fail closed on ambiguous semantic mappings.
- Do not introduce unrestricted database access or financial write actions without an explicit milestone change.
- Any new financial metric, mapping rule, or validator requires tests.

## CI and runners

Core CI runs on GitHub-hosted runners. Do not configure `self-hosted` runners for project CI. The default runner is `ubuntu-latest`; checkout and Python setup use GitHub-maintained actions.

## Pull requests

A pull request should contain one bounded capability or correction. Include:

- what changed;
- why the boundary is appropriate;
- financial semantics affected, if any;
- trust/safety boundary impact;
- tests and CI evidence;
- explicit non-goals/follow-up work.

Before requesting review, refresh `docs/HANDOFF.md` when the branch changes the canonical project state.
