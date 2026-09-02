from decimal import Decimal

from xuanmoney.domain import IncomeStatement
from xuanmoney.finance.profit_bridge import profit_bridge, validate_profit_bridge
from xuanmoney.service import analyze_financials


def statement(
    period: str,
    *,
    revenue: str = "1000",
    cogs: str = "600",
    operating_expenses: str = "100",
    other_income: str = "10",
    other_expenses: str = "5",
    taxes: str = "20",
) -> IncomeStatement:
    return IncomeStatement(
        period=period,
        source=f"fixture:{period}",
        revenue=Decimal(revenue),
        cogs=Decimal(cogs),
        operating_expenses=Decimal(operating_expenses),
        other_income=Decimal(other_income),
        other_expenses=Decimal(other_expenses),
        taxes=Decimal(taxes),
    )


def test_profit_bridge_signs_and_exact_reconciliation() -> None:
    previous = statement("2026-07")
    current = statement(
        "2026-08",
        revenue="1100",
        cogs="650",
        operating_expenses="120",
        other_income="5",
        other_expenses="10",
        taxes="25",
    )

    bridge = profit_bridge(current, previous)
    contributions = {item.component: item.contribution for item in bridge.contributions}

    assert contributions == {
        "revenue": Decimal("100"),
        "cogs": Decimal("-50"),
        "operating_expenses": Decimal("-20"),
        "other_income": Decimal("-5"),
        "other_expenses": Decimal("-5"),
        "taxes": Decimal("-5"),
    }
    assert bridge.total_net_profit_change == Decimal("15")
    assert sum(contributions.values(), start=Decimal("0")) == Decimal("15")
    assert bridge.reconciliation_difference == Decimal("0")
    assert bridge.reconciled is True
    assert validate_profit_bridge(bridge).passed is True


def test_cost_and_expense_decreases_improve_profit() -> None:
    previous = statement("2026-07")
    current = statement(
        "2026-08",
        cogs="550",
        operating_expenses="80",
        other_expenses="3",
        taxes="15",
    )

    bridge = profit_bridge(current, previous)
    contributions = {item.component: item.contribution for item in bridge.contributions}

    assert contributions["cogs"] == Decimal("50")
    assert contributions["operating_expenses"] == Decimal("20")
    assert contributions["other_expenses"] == Decimal("2")
    assert contributions["taxes"] == Decimal("5")
    assert bridge.total_net_profit_change == Decimal("77")
    assert bridge.reconciled is True


def test_profit_bridge_preserves_both_periods_of_evidence() -> None:
    previous = statement("2026-07")
    current = statement("2026-08", revenue="900")

    bridge = profit_bridge(current, previous)
    revenue = next(item for item in bridge.contributions if item.component == "revenue")

    assert [item.period for item in revenue.evidence] == ["2026-07", "2026-08"]
    assert [item.source for item in revenue.evidence] == [
        "fixture:2026-07",
        "fixture:2026-08",
    ]


def test_validator_fails_when_bridge_is_tampered() -> None:
    bridge = profit_bridge(statement("2026-08"), statement("2026-07"))
    tampered = bridge.model_copy(update={"reconciliation_difference": Decimal("1")})

    validation = validate_profit_bridge(tampered)

    assert validation.passed is False
    assert "differs" in validation.details


def test_service_emits_reconciled_profit_bridge() -> None:
    state = analyze_financials(
        query="Why did net profit change?",
        current=statement("2026-08", revenue="900"),
        previous=statement("2026-07"),
    )

    assert state.result is not None
    assert state.result.profit_bridge is not None
    assert state.result.profit_bridge.total_net_profit_change == Decimal("-100")
    assert state.result.profit_bridge.reconciled is True
    validation = next(
        item
        for item in state.result.validations
        if item.name == "profit_bridge_reconciliation"
    )
    assert validation.passed is True
