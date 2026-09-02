from __future__ import annotations

from decimal import Decimal

from xuanmoney.domain import (
    Evidence,
    IncomeStatement,
    ProfitBridgeContribution,
    ProfitBridgeResult,
    ValidationResult,
)
from xuanmoney.finance.metrics import net_profit


_COMPONENT_SIGNS: tuple[tuple[str, Decimal], ...] = (
    ("revenue", Decimal("1")),
    ("cogs", Decimal("-1")),
    ("operating_expenses", Decimal("-1")),
    ("other_income", Decimal("1")),
    ("other_expenses", Decimal("-1")),
    ("taxes", Decimal("-1")),
)


def _evidence(statement: IncomeStatement, field: str) -> Evidence:
    return Evidence(
        source=statement.source,
        field=field,
        period=statement.period,
        value=getattr(statement, field),
    )


def profit_bridge(
    current: IncomeStatement,
    previous: IncomeStatement,
) -> ProfitBridgeResult:
    """Decompose period-to-period net-profit change into signed line-item effects.

    A positive contribution improves net profit relative to the previous period. A
    negative contribution reduces it. Expense/cost increases therefore have negative
    contributions, while decreases have positive contributions.
    """

    contributions: list[ProfitBridgeContribution] = []
    for field, sign in _COMPONENT_SIGNS:
        current_value = getattr(current, field)
        previous_value = getattr(previous, field)
        raw_change = current_value - previous_value
        contributions.append(
            ProfitBridgeContribution(
                component=field,
                raw_change=raw_change,
                contribution=sign * raw_change,
                evidence=[
                    _evidence(previous, field),
                    _evidence(current, field),
                ],
            )
        )

    total_change = net_profit(current).value - net_profit(previous).value
    contribution_sum = sum(
        (item.contribution for item in contributions),
        start=Decimal("0"),
    )
    return ProfitBridgeResult(
        current_period=current.period,
        previous_period=previous.period,
        total_net_profit_change=total_change,
        contributions=contributions,
        reconciliation_difference=total_change - contribution_sum,
    )


def validate_profit_bridge(bridge: ProfitBridgeResult) -> ValidationResult:
    difference = bridge.reconciliation_difference
    return ValidationResult(
        name="profit_bridge_reconciliation",
        passed=difference == 0,
        details=(
            "profit bridge reconciles exactly to net-profit change"
            if difference == 0
            else f"profit bridge differs from net-profit change by {difference}"
        ),
    )
