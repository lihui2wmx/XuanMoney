from __future__ import annotations

from decimal import Decimal

from xuanmoney.domain import MetricResult, VarianceResult


def compare_metric(current: MetricResult, previous: MetricResult) -> VarianceResult:
    if current.name != previous.name:
        raise ValueError("cannot compare metrics with different names")

    absolute_change = current.value - previous.value
    relative_change = None
    if previous.value != 0:
        relative_change = absolute_change / abs(previous.value)

    return VarianceResult(
        metric=current.name,
        current=current.value,
        previous=previous.value,
        absolute_change=absolute_change,
        relative_change=relative_change,
    )


def compare_metric_sets(
    current: list[MetricResult],
    previous: list[MetricResult],
) -> list[VarianceResult]:
    previous_by_name = {item.name: item for item in previous}
    results: list[VarianceResult] = []

    for item in current:
        prior = previous_by_name.get(item.name)
        if prior is not None:
            results.append(compare_metric(item, prior))

    return results
