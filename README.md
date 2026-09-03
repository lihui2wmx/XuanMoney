# XuanMoney

XuanMoney is an evidence-first AI finance agent project focused on trustworthy financial analysis rather than free-form financial chat.

## Design principles

- **LLM for bounded intent, approved tool selection, and explanation.**
- **Deterministic code for financial calculations, semantic mapping, validation, and reconciliation.**
- **A fixed read-only tool registry between models and finance services.**
- **A bounded runtime owns execution policy; provider layers own model I/O only.**
- **No unrestricted database, filesystem, Python, shell, or financial write access from the model.**
- **Evidence-first outputs: material claims remain traceable to source data and calculations.**
- **Fail closed on ambiguous financial semantics instead of asking an LLM to guess.**
- **Human approval plus separate governance for any future high-risk financial action.**

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
11. expose `analyze_financials` and `analyze_dimension` through a fixed typed read-only tool registry;
12. publish Pydantic JSON Schemas and stable tool failure codes;
13. execute a bounded single-plan / at-most-one-tool / single-synthesis runtime through `ModelPort`;
14. expose a provider-neutral `ModelProvider.complete()` transport contract;
15. bridge the runtime-facing `ModelPort` to `ModelProvider` with deterministic JSON transport while preserving runtime-owned validation;
16. select provider factories through an immutable application-owned allowlist;
17. resolve injected environment credential references through a protected credential boundary;
18. construct an OpenAI Responses API provider through a trusted factory with configured timeout and SDK retries disabled;
19. map the existing `ModelRequest(prompt, context)` contract into one synchronous Responses API call and normalize provider failures into stable safe codes.

Out of scope: payments, journal posting, tax filing, ERP write-back, autonomous financial execution, unrestricted SQL, arbitrary model filesystem/code execution, model-guessed business semantics, production authentication, provider-native autonomous tools, retry/fallback, and financial writes.

## Architecture

```text
Application-owned CSV / XLSX ingestion
             |
             v
Semantic Registry + Normalized Domain Models
             |
             +--> Finance analysis
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
 Controlled Analysis Tool Registry
   - analyze_financials
   - analyze_dimension
             ^
             |
      BoundedModelRuntime
             |
             v
          ModelPort
             |
             v
  ModelPortProviderBridge
             |
             v
       ModelProvider
             |
             v
 ProviderFactoryRegistry
             |
             v
 OpenAIProviderFactory
             |
             v
 OpenAIProviderAdapter
             |
             v
 OpenAI Responses API
```

The OpenAI adapter and official SDK dependency are integrated, but normal CI uses deterministic fake SDK clients and no live API credential or network call. A reusable application-owned runtime composition/bootstrap boundary is not yet implemented.

## Development setup

Requires Python 3.12+.

```bash
python -m pip install -e ".[dev]"
pytest
```

## Income-statement ingestion

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

The source must explicitly provide `dimension` and `member` semantics. A column named `product`, `department`, or similar is not silently interpreted as a dimension.

## Controlled analysis tools

```python
from xuanmoney.tools import build_analysis_tool_registry

registry = build_analysis_tool_registry()
print(registry.names())
# ('analyze_financials', 'analyze_dimension')

schemas = registry.metadata()
```

The model-callable registry deliberately excludes `load_income_statements`, `load_dimensional_rows`, SQL, Python/shell execution, dynamic imports, and financial write operations. See [`docs/TOOLS.md`](docs/TOOLS.md).

## Provider integration

The first integrated real provider boundary is OpenAI Responses API. Provider configuration remains non-secret, credentials are resolved through the application-owned credential boundary, and the OpenAI SDK client is constructed with automatic retries disabled.

Normal tests and GitHub Actions do not require an OpenAI API key and do not issue live provider requests. See [`docs/OPENAI_PROVIDER_ADAPTER.md`](docs/OPENAI_PROVIDER_ADAPTER.md).

## Contributing and AI handoff

Start with:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/HANDOFF.md`](docs/HANDOFF.md)
3. [`docs/AI_WORKFLOW.md`](docs/AI_WORKFLOW.md)
4. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
5. [`docs/TOOLS.md`](docs/TOOLS.md)
6. [`docs/RUNTIME.md`](docs/RUNTIME.md)
7. [`docs/PROVIDER_CONTRACT.md`](docs/PROVIDER_CONTRACT.md)
8. [`docs/PROVIDER_SAFETY.md`](docs/PROVIDER_SAFETY.md)
9. [`docs/CREDENTIALS.md`](docs/CREDENTIALS.md)
10. [`docs/PROVIDER_COMPOSITION.md`](docs/PROVIDER_COMPOSITION.md)
11. [`docs/PROVIDER_REGISTRY.md`](docs/PROVIDER_REGISTRY.md)
12. [`docs/OPENAI_PROVIDER_ADAPTER.md`](docs/OPENAI_PROVIDER_ADAPTER.md)
13. [`CONTRIBUTING.md`](CONTRIBUTING.md)

`docs/HANDOFF.md` is the canonical current-state checkpoint so a new AI agent or contributor can continue without previous conversation context.

Core CI uses GitHub-hosted runners (`ubuntu-latest`) and GitHub-maintained setup actions. Self-hosted runners are not used for project CI.

## License

XuanMoney is licensed under the [Apache License 2.0](LICENSE).
