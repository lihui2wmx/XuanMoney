from decimal import Decimal

from xuanmoney.domain import BalanceSheet, IncomeStatement
from xuanmoney.finance.metrics import gross_margin, net_profit
from xuanmoney.finance.validation import validate_balance_sheet
from xuanmoney.service import analyze_financials


def statement(period: str, revenue: str, cogs: str) -> IncomeStatement:
    return IncomeStatement(
        period=period,
        revenue=Decimal(revenue),
        cogs=Decimal(cogs),
        operating_expenses=Decimal("100"),
        other_income=Decimal("10"),
        other_expenses=Decimal("5"),
        taxes=Decimal("20"),
    )


def test_profitability_metrics_are_deterministic() -> None:
    item = statement("2026-08", "1000", "600")

    assert gross_margin(item).value == Decimal("0.4")
    assert net_profit(item).value == Decimal("285")


def test_balance_sheet_identity() -> None:
    valid = BalanceSheet(
        period="2026-08",
        assets=Decimal("1000"),
        liabilities=Decimal("600"),
        equity=Decimal("400"),
    )
    invalid = valid.model_copy(update={"equity": Decimal("399")})

    assert validate_balance_sheet(valid).passed is True
    assert validate_balance_sheet(invalid).passed is False


def test_analysis_emits_decline_findings() -> None:
    current = statement("2026-08", "900", "600")
    previous = statement("2026-07", "1000", "600")

    state = analyze_financials(
        query="Why did profitability decline?",
        current=current,
        previous=previous,
    )

    assert state.phase.value == "complete"
    assert state.result is not None
    codes = {finding.code for finding in state.result.findings}
    assert "NET_PROFIT_DECLINE" in codes
    assert "GROSS_MARGIN_DECLINE" in codes
