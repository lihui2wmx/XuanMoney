from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable

from xuanmoney.domain import (
    DimensionalMemberContribution,
    DimensionalMemberMetrics,
    DimensionalRow,
    DimensionalVarianceResult,
    Evidence,
    ValidationResult,
)


def _row_evidence(row: DimensionalRow, field: str) -> Evidence:
    return Evidence(
        source=row.source,
        field=field,
        period=row.period,
        value=getattr(row, field),
        dimension=row.dimension,
        member=row.member,
    )


def aggregate_dimension(
    rows: Iterable[DimensionalRow],
    *,
    period: str,
    dimension: str,
) -> list[DimensionalMemberMetrics]:
    """Aggregate one named dimension for one period.

    Aggregation is deliberately single-dimensional. Rows for other dimensions or
    periods are ignored. Mixed currencies inside the selected slice fail closed because
    summing them would create an invalid financial total without an FX policy.
    """

    selected = [
        row for row in rows if row.period == period and row.dimension == dimension
    ]
    if not selected:
        return []

    currencies = {row.currency for row in selected}
    if len(currencies) != 1:
        raise ValueError(
            f"dimension {dimension!r} period {period!r} contains mixed currencies: "
            f"{sorted(currencies)}"
        )
    currency = next(iter(currencies))

    grouped: dict[str, list[DimensionalRow]] = defaultdict(list)
    for row in selected:
        grouped[row.member].append(row)

    results: list[DimensionalMemberMetrics] = []
    for member in sorted(grouped):
        member_rows = grouped[member]
        revenue = sum((row.revenue for row in member_rows), start=Decimal("0"))
        cogs = sum((row.cogs for row in member_rows), start=Decimal("0"))
        gross_profit = revenue - cogs
        gross_margin = None if revenue == 0 else gross_profit / revenue

        evidence: list[Evidence] = []
        for row in member_rows:
            evidence.extend(
                [
                    _row_evidence(row, "revenue"),
                    _row_evidence(row, "cogs"),
                ]
            )

        results.append(
            DimensionalMemberMetrics(
                period=period,
                dimension=dimension,
                member=member,
                currency=currency,
                revenue=revenue,
                cogs=cogs,
                gross_profit=gross_profit,
                gross_margin=gross_margin,
                evidence=evidence,
            )
        )

    return results


def compare_dimension_members(
    *,
    dimension: str,
    current_period: str,
    previous_period: str,
    current: Iterable[DimensionalMemberMetrics],
    previous: Iterable[DimensionalMemberMetrics],
) -> DimensionalVarianceResult:
    """Reconcile gross-profit change across members of one dimension.

    Missing members are treated as zero in the absent period. This supports both new
    and disappearing members without inventing values or dropping their contribution.
    """

    current_by_member = {item.member: item for item in current}
    previous_by_member = {item.member: item for item in previous}
    members = sorted(current_by_member.keys() | previous_by_member.keys())

    contributions: list[DimensionalMemberContribution] = []
    for member in members:
        current_item = current_by_member.get(member)
        previous_item = previous_by_member.get(member)

        current_revenue = current_item.revenue if current_item is not None else Decimal("0")
        previous_revenue = (
            previous_item.revenue if previous_item is not None else Decimal("0")
        )
        current_cogs = current_item.cogs if current_item is not None else Decimal("0")
        previous_cogs = previous_item.cogs if previous_item is not None else Decimal("0")

        revenue_change = current_revenue - previous_revenue
        cogs_change = current_cogs - previous_cogs
        gross_profit_change = revenue_change - cogs_change

        evidence: list[Evidence] = []
        if previous_item is not None:
            evidence.extend(previous_item.evidence)
        if current_item is not None:
            evidence.extend(current_item.evidence)

        contributions.append(
            DimensionalMemberContribution(
                member=member,
                revenue_change=revenue_change,
                cogs_change=cogs_change,
                gross_profit_change=gross_profit_change,
                evidence=evidence,
            )
        )

    current_total = sum(
        (item.gross_profit for item in current_by_member.values()),
        start=Decimal("0"),
    )
    previous_total = sum(
        (item.gross_profit for item in previous_by_member.values()),
        start=Decimal("0"),
    )
    total_change = current_total - previous_total
    contribution_sum = sum(
        (item.gross_profit_change for item in contributions),
        start=Decimal("0"),
    )

    return DimensionalVarianceResult(
        dimension=dimension,
        current_period=current_period,
        previous_period=previous_period,
        total_gross_profit_change=total_change,
        member_contributions=contributions,
        reconciliation_difference=total_change - contribution_sum,
    )


def validate_dimensional_variance(
    variance: DimensionalVarianceResult,
) -> ValidationResult:
    difference = variance.reconciliation_difference
    return ValidationResult(
        name="dimensional_gross_profit_reconciliation",
        passed=difference == 0,
        details=(
            "member gross-profit contributions reconcile exactly to dimension total"
            if difference == 0
            else f"member contributions differ from dimension total by {difference}"
        ),
    )
