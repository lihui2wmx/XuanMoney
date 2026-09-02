# XuanMoney

XuanMoney is an evidence-first AI finance agent project focused on trustworthy financial analysis rather than free-form financial chat.

## Design principles

- **LLM for intent, planning, drill-down selection, and explanation.**
- **Deterministic code for financial calculations, semantic mapping, and validation.**
- **Structured read-only tools for data access; no unrestricted database access from the model.**
- **Evidence-first outputs: material claims remain traceable to source data and calculations.**
- **Fail closed on ambiguous financial semantics instead of asking an LLM to guess.**
- **Human approval for any future high-risk financial action.**

## Current capabilities

The current read-only finance-analysis core can:

1. ingest normalized income-statement data from CSV and XLSX;
2. map explicit Chinese/English column aliases into canonical finance schemas;
3. preserve file/worksheet/row provenance;
4. compute core profitability metrics with `Decimal` arithmetic;
5. perform period-over-period variance analysis;
6. decompose net-profit change with an exactly reconciled deterministic profit bridge;
7. ingest explicit one-dimensional business rows (`period/dimension/member/revenue/cogs`);
8. aggregate member revenue, COGS, gross profit, and gross margin for one named dimension;
9. reconcile member gross-profit changes to the selected dimension total across periods;
10. validate accounting identities and deterministic reconciliations;
11. expose the workflows through typed Python service/domain boundaries.

Out of scope: payments, journal posting, tax filing, ERP write-back, autonomous financial execution, unrestricted SQL, model-guessed business semantics, and production authentication.

## Architecture

```text
CSV / XLSX / normalized input
             |
             v
Semantic Registry + Ingestion Adapter
             |
             +--> IncomeStatement analysis
             |      - profitability metrics
             |      - period variance
             |      - profit bridge
             |
             +--> One-dimensional business analysis
                    - member aggregation
                    - gross-profit / gross-margin metrics
                    - member contribution reconciliation
             |
             v
          Validators
             |
             v
 Evidence-backed structured results
             |
             v
 Future controlled tool layer / LLM planner
```

The LLM layer is intentionally not implemented yet. Financial facts, formulas, semantic mappings, and reconciliation are stabilized first.

## Development setup

Requires Python 3.12+.

```bash
python -m pip install -e ".[dev]"
pytest
```

## Income-statement ingestion

Example CSV:

```csv
period,revenue,cogs,operating_expenses,taxes
2026-07,1000,600,100,20
2026-08,900,600,100,20
```

```python
from xuanmoney.ingestion import load_income_statements

statements = load_income_statements("income.csv")
```

## One-dimensional business analysis

The canonical dimensional contract is explicit:

```csv
period,dimension,member,revenue,cogs
2026-07,product,A,100,60
2026-07,product,B,50,30
2026-08,product,A,120,70
2026-08,product,C,30,10
```

```python
from xuanmoney.ingestion import load_dimensional_rows
from xuanmoney.service import analyze_dimension

rows = load_dimensional_rows("business.csv")
result = analyze_dimension(
    rows=rows,
    dimension="product",
    current_period="2026-08",
    previous_period="2026-07",
)
```

The source must explicitly provide `dimension` and `member` semantics. A column named `product`, `department`, or similar is not silently interpreted as a dimension. Unknown columns are ignored rather than guessed.

## Contributing and AI handoff

Start with:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/HANDOFF.md`](docs/HANDOFF.md)
3. [`docs/AI_WORKFLOW.md`](docs/AI_WORKFLOW.md)
4. [`CONTRIBUTING.md`](CONTRIBUTING.md)

`docs/HANDOFF.md` is the canonical current-state checkpoint so a new AI agent or contributor can continue without previous conversation context.

Core CI uses GitHub-hosted runners (`ubuntu-latest`) and GitHub-maintained setup actions. Self-hosted runners are not used for project CI.

## License

XuanMoney is licensed under the [Apache License 2.0](LICENSE).
