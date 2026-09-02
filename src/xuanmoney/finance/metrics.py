from __future__ import annotations

from decimal import Decimal

from xuanmoney.domain import Evidence, IncomeStatement, MetricResult, Unit


def _evidence(statement: IncomeStatement, field: str) -> Evidence:
    return Evidence(
        source="income_statement",
        field=field,
        period=statement.period,
        value=getattr(statement, field),
    )


def gross_profit(statement: IncomeStatement) -> MetricResult:
    value = statement.revenue - statement.cogs
    return MetricResult(
        name="gross_profit",
        value=value,
        unit=Unit.MONEY,
        evidence=[_evidence(statement, "revenue"), _evidence(statement, "cogs")],
    )


def gross_margin(statement: IncomeStatement) -> MetricResult:
    if statement.revenue == 0:
        raise ValueError("gross_margin is undefined when revenue is zero")
    gross = gross_profit(statement)
    return MetricResult(
        name="gross_margin",
        value=gross.value / statement.revenue,
        unit=Unit.RATIO,
        evidence=gross.evidence,
    )


def operating_profit(statement: IncomeStatement) -> MetricResult:
    gross = gross_profit(statement)
    value = gross.value - statement.operating_expenses
    return MetricResult(
        name="operating_profit",
        value=value,
        unit=Unit.MONEY,
        evidence=[*gross.evidence, _evidence(statement, "operating_expenses")],
    )


def net_profit(statement: IncomeStatement) -> MetricResult:
    operating = operating_profit(statement)
    value = (
        operating.value
        + statement.other_income
        - statement.other_expenses
        - statement.taxes
    )
    return MetricResult(
        name="net_profit",
        value=value,
        unit=Unit.MONEY,
        evidence=[
            *operating.evidence,
            _evidence(statement, "other_income"),
            _evidence(statement, "other_expenses"),
            _evidence(statement, "taxes"),
        ],
    )


def profitability_metrics(statement: IncomeStatement) -> list[MetricResult]:
    return [
        gross_profit(statement),
        gross_margin(statement),
        operating_profit(statement),
        net_profit(statement),
    ]
