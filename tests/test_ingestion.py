from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import Workbook

from xuanmoney.ingestion import TabularIngestionError, income_statements_from_rows, load_income_statements
from xuanmoney.semantic import resolve_income_statement_columns


def test_semantic_registry_resolves_explicit_chinese_aliases() -> None:
    mapping = resolve_income_statement_columns(["会计期间", "营业收入", "营业成本", "所得税费用"])

    assert mapping == {
        "period": "会计期间",
        "revenue": "营业收入",
        "cogs": "营业成本",
        "taxes": "所得税费用",
    }


def test_semantic_registry_fails_on_ambiguous_revenue_columns() -> None:
    with pytest.raises(TabularIngestionError, match="multiple source columns"):
        income_statements_from_rows(
            [
                {
                    "期间": "2026-08",
                    "营业收入": "1000",
                    "销售收入": "1000",
                    "营业成本": "600",
                }
            ]
        )


def test_rows_are_normalized_without_llm_inference() -> None:
    statements = income_statements_from_rows(
        [
            {
                "期间": "2026-08",
                "币种": "CNY",
                "营业收入": "1,000.50",
                "营业成本": "600.25",
                "运营费用": "100",
                "所得税费用": "20",
                "ignored column": "not interpreted",
            }
        ],
        source="fixture",
    )

    assert len(statements) == 1
    statement = statements[0]
    assert statement.period == "2026-08"
    assert statement.revenue == Decimal("1000.50")
    assert statement.cogs == Decimal("600.25")
    assert statement.operating_expenses == Decimal("100")
    assert statement.taxes == Decimal("20")
    assert statement.source == "fixture:row:2"


def test_csv_ingestion_preserves_source_provenance(tmp_path: Path) -> None:
    path = tmp_path / "income.csv"
    path.write_text(
        "period,revenue,cogs,operating_expenses\n2026-08,1000,600,100\n",
        encoding="utf-8",
    )

    statements = load_income_statements(path)

    assert statements[0].revenue == Decimal("1000")
    assert statements[0].source == "income.csv:row:2"


def test_xlsx_ingestion_uses_same_semantic_contract(tmp_path: Path) -> None:
    path = tmp_path / "income.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "利润表"
    sheet.append(["月份", "营业收入", "营业成本", "运营费用"])
    sheet.append(["2026-08", 1000, 600, 100])
    workbook.save(path)
    workbook.close()

    statements = load_income_statements(path, sheet_name="利润表")

    assert statements[0].period == "2026-08"
    assert statements[0].revenue == Decimal("1000")
    assert statements[0].source == "income.xlsx:利润表:row:2"


def test_missing_required_column_fails_closed() -> None:
    with pytest.raises(TabularIngestionError, match="required canonical field 'cogs'"):
        income_statements_from_rows([{"period": "2026-08", "revenue": "1000"}])
