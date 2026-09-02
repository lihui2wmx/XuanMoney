from decimal import Decimal

import pytest

from xuanmoney.domain import DimensionalRow
from xuanmoney.finance.dimensional import aggregate_dimension
from xuanmoney.ingestion import (
    TabularIngestionError,
    dimensional_rows_from_rows,
    load_dimensional_rows,
)
from xuanmoney.service import analyze_dimension


def dimensional_row(
    period: str,
    member: str,
    revenue: str,
    cogs: str,
    *,
    dimension: str = "product",
    currency: str = "CNY",
    source: str | None = None,
) -> DimensionalRow:
    return DimensionalRow(
        period=period,
        dimension=dimension,
        member=member,
        currency=currency,
        source=source or f"fixture:{period}:{member}",
        revenue=Decimal(revenue),
        cogs=Decimal(cogs),
    )


def test_aggregation_is_deterministic_and_preserves_provenance() -> None:
    rows = [
        dimensional_row("2026-08", "A", "100", "60", source="sales.csv:row:2"),
        dimensional_row("2026-08", "A", "50", "20", source="sales.csv:row:3"),
        dimensional_row("2026-08", "B", "0", "10", source="sales.csv:row:4"),
        dimensional_row("2026-08", "ignored", "999", "1", dimension="region"),
    ]

    metrics = aggregate_dimension(rows, period="2026-08", dimension="product")
    by_member = {item.member: item for item in metrics}

    assert by_member["A"].revenue == Decimal("150")
    assert by_member["A"].cogs == Decimal("80")
    assert by_member["A"].gross_profit == Decimal("70")
    assert by_member["A"].gross_margin == Decimal("70") / Decimal("150")
    assert {item.source for item in by_member["A"].evidence} == {
        "sales.csv:row:2",
        "sales.csv:row:3",
    }

    assert by_member["B"].gross_profit == Decimal("-10")
    assert by_member["B"].gross_margin is None


def test_period_comparison_handles_new_and_disappearing_members() -> None:
    rows = [
        dimensional_row("2026-07", "A", "100", "60"),
        dimensional_row("2026-07", "B", "50", "30"),
        dimensional_row("2026-08", "A", "120", "70"),
        dimensional_row("2026-08", "C", "30", "10"),
    ]

    result = analyze_dimension(
        rows=rows,
        dimension="product",
        current_period="2026-08",
        previous_period="2026-07",
    )

    assert result.variance is not None
    assert result.validation_passed is True
    assert result.variance.reconciled is True
    assert result.variance.total_gross_profit_change == Decimal("10")

    contributions = {
        item.member: item.gross_profit_change
        for item in result.variance.member_contributions
    }
    assert contributions == {
        "A": Decimal("10"),
        "B": Decimal("-20"),
        "C": Decimal("20"),
    }
    assert sum(contributions.values(), start=Decimal("0")) == Decimal("10")


def test_dimensional_ingestion_uses_explicit_chinese_aliases() -> None:
    rows = [
        {
            "会计期间": "2026-08",
            "维度": "product",
            "成员": "A",
            "营业收入": "1,200.50",
            "营业成本": "700.25",
            "币种": "CNY",
            "备注": "ignored",
        }
    ]

    parsed = dimensional_rows_from_rows(rows, source="fixture")

    assert parsed[0].period == "2026-08"
    assert parsed[0].dimension == "product"
    assert parsed[0].member == "A"
    assert parsed[0].revenue == Decimal("1200.50")
    assert parsed[0].cogs == Decimal("700.25")
    assert parsed[0].source == "fixture:row:2"


def test_dimensional_ingestion_fails_closed_without_member_semantics() -> None:
    rows = [
        {
            "period": "2026-08",
            "dimension": "product",
            "product": "A",
            "revenue": "100",
            "cogs": "60",
        }
    ]

    with pytest.raises(TabularIngestionError, match="member"):
        dimensional_rows_from_rows(rows)


def test_csv_dimensional_loader_preserves_file_row_source(tmp_path) -> None:
    path = tmp_path / "business.csv"
    path.write_text(
        "period,dimension,member,revenue,cogs\n"
        "2026-08,product,A,100,60\n",
        encoding="utf-8",
    )

    rows = load_dimensional_rows(path)

    assert len(rows) == 1
    assert rows[0].source == "business.csv:row:2"


def test_analysis_fails_closed_on_cross_period_currency_mismatch() -> None:
    rows = [
        dimensional_row("2026-07", "A", "100", "60", currency="CNY"),
        dimensional_row("2026-08", "A", "120", "70", currency="USD"),
    ]

    with pytest.raises(ValueError, match="different currencies"):
        analyze_dimension(
            rows=rows,
            dimension="product",
            current_period="2026-08",
            previous_period="2026-07",
        )


def test_analysis_requires_current_dimension_slice() -> None:
    with pytest.raises(ValueError, match="no rows found"):
        analyze_dimension(
            rows=[dimensional_row("2026-07", "A", "100", "60")],
            dimension="product",
            current_period="2026-08",
        )
