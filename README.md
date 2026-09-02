# XuanMoney

XuanMoney is an evidence-first AI finance agent project focused on trustworthy financial analysis rather than free-form financial chat.

## Design principles

- **LLM for intent, planning, drill-down selection, and explanation.**
- **Deterministic code for financial calculations, semantic mapping, and validation.**
- **Structured read-only tools for data access; no unrestricted database access from the model.**
- **Evidence-first outputs: material claims remain traceable to source data and calculations.**
- **Fail closed on ambiguous financial semantics instead of asking an LLM to guess.**
- **Human approval for any future high-risk financial action.**

## Current v0.1 capabilities

The active milestone is a read-only Finance Analysis Agent core that can:

1. ingest normalized income-statement data from CSV and XLSX;
2. map explicit Chinese/English column aliases into a canonical finance schema;
3. preserve file/worksheet/row provenance;
4. compute core profitability metrics with `Decimal` arithmetic;
5. perform period-over-period variance analysis;
6. decompose net-profit change with an exactly reconciled deterministic profit bridge;
7. validate accounting identities and bridge reconciliation;
8. produce structured findings with evidence;
9. expose the workflow through typed Python service/domain boundaries.

Out of scope for v0.1: payments, journal posting, tax filing, ERP write-back, autonomous financial execution, unrestricted SQL, and production authentication.

## Architecture

```text
CSV / XLSX / normalized input
             |
             v
Semantic Registry + Ingestion Adapter
             |
             v
       FinanceAgentState
             |
             v
        Finance Kernel
   - profitability metrics
   - period variance
   - profit bridge
             |
             v
          Validator
             |
             v
 Evidence-backed AnalysisResult
             |
             v
 Future LLM planner / synthesizer
```

The LLM layer is intentionally not implemented yet. Financial facts, formulas, semantic mappings, and reconciliation are stabilized first.

## Development setup

Requires Python 3.12+.

```bash
python -m pip install -e ".[dev]"
pytest
```

## Tabular ingestion

Example CSV:

```csv
period,revenue,cogs,operating_expenses,taxes
2026-07,1000,600,100,20
2026-08,900,600,100,20
```

Load it through the deterministic ingestion boundary:

```python
from xuanmoney.ingestion import load_income_statements

statements = load_income_statements("income.csv")
```

Chinese headers such as `会计期间`, `营业收入`, `营业成本`, and `所得税费用` are supported only when explicitly registered in `src/xuanmoney/semantic/registry.py`. Unknown columns are not guessed into financial fields.

## Contributing and AI handoff

Start with:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/HANDOFF.md`](docs/HANDOFF.md)
3. [`docs/AI_WORKFLOW.md`](docs/AI_WORKFLOW.md)
4. [`CONTRIBUTING.md`](CONTRIBUTING.md)

`docs/HANDOFF.md` is the canonical current-state checkpoint so a new AI agent or contributor can continue without previous conversation context.

Core CI uses GitHub-hosted runners (`ubuntu-latest`) and GitHub-maintained setup actions. Self-hosted runners are not used for project CI.
