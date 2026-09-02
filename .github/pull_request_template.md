## Bounded change

<!-- Describe the single capability/correction implemented by this PR. -->

## Financial semantics

<!-- List formulas, metric definitions, mappings, or accounting rules changed. Write "None" if unchanged. -->

## Trust boundary impact

<!-- Confirm whether this remains read-only and whether permissions/data-access behavior changed. -->

- [ ] No financial write capability was introduced.
- [ ] No accounting formula or semantic mapping is delegated to free-form LLM reasoning.
- [ ] Material calculated results preserve evidence/provenance.

## Verification

<!-- Include exact commands and CI result. -->

```bash
python -m pip install -e ".[dev]"
pytest
```

- [ ] Tests pass locally or an explanation is provided.
- [ ] GitHub Actions CI passes on a GitHub-hosted runner.

## Handoff

- [ ] `docs/HANDOFF.md` reflects the branch state when this PR changes the canonical project state.
- [ ] `docs/DEVELOPMENT_LOG.md` was updated for milestone-level changes.

## Non-goals / follow-up

<!-- Explicitly state what this PR does not attempt to solve and the recommended next bounded increment. -->
