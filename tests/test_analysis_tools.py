from decimal import Decimal

import pytest

from xuanmoney.agent.state import FinanceAgentState
from xuanmoney.domain import DimensionalAnalysisResult
from xuanmoney.tools import (
    ToolErrorCode,
    ToolInvocationError,
    ToolRisk,
    build_analysis_tool_registry,
)


def test_registry_exposes_only_fixed_read_only_analysis_tools() -> None:
    registry = build_analysis_tool_registry()

    assert registry.names() == ("analyze_financials", "analyze_dimension")
    assert not hasattr(registry, "register")

    metadata = {item.name: item for item in registry.metadata()}
    assert set(metadata) == {"analyze_financials", "analyze_dimension"}
    assert all(item.risk is ToolRisk.READ_ONLY for item in metadata.values())
    assert all(item.model_callable is True for item in metadata.values())
    assert "properties" in metadata["analyze_financials"].request_schema
    assert "properties" in metadata["analyze_dimension"].response_schema


def test_financial_analysis_tool_accepts_normalized_typed_payload() -> None:
    registry = build_analysis_tool_registry()

    result = registry.invoke(
        "analyze_financials",
        {
            "query": "compare profitability",
            "current": {
                "period": "2026-08",
                "revenue": "1000",
                "cogs": "600",
                "operating_expenses": "100",
                "taxes": "20",
            },
            "previous": {
                "period": "2026-07",
                "revenue": "900",
                "cogs": "550",
                "operating_expenses": "90",
                "taxes": "18",
            },
        },
    )

    assert isinstance(result, FinanceAgentState)
    assert result.phase.value == "complete"
    assert result.result is not None
    assert result.result.profit_bridge is not None
    assert result.result.profit_bridge.reconciled is True


def test_dimensional_analysis_tool_returns_structured_reconciled_result() -> None:
    registry = build_analysis_tool_registry()

    result = registry.invoke(
        "analyze_dimension",
        {
            "dimension": "product",
            "current_period": "2026-08",
            "previous_period": "2026-07",
            "rows": [
                {
                    "period": "2026-07",
                    "dimension": "product",
                    "member": "A",
                    "revenue": "100",
                    "cogs": "60",
                },
                {
                    "period": "2026-08",
                    "dimension": "product",
                    "member": "A",
                    "revenue": "120",
                    "cogs": "70",
                },
            ],
        },
    )

    assert isinstance(result, DimensionalAnalysisResult)
    assert result.variance is not None
    assert result.variance.total_gross_profit_change == Decimal("10")
    assert result.variance.reconciled is True
    assert result.validation_passed is True


def test_unknown_or_filesystem_tool_name_fails_closed() -> None:
    registry = build_analysis_tool_registry()

    for name in ("load_income_statements", "python", "sql", "delete_voucher"):
        with pytest.raises(ToolInvocationError) as captured:
            registry.invoke(name, {})
        assert captured.value.failure.code is ToolErrorCode.UNKNOWN_TOOL
        assert captured.value.failure.tool == name


def test_invalid_request_has_typed_failure_without_echoing_input() -> None:
    registry = build_analysis_tool_registry()

    with pytest.raises(ToolInvocationError) as captured:
        registry.invoke(
            "analyze_dimension",
            {
                "dimension": "product",
                "current_period": "2026-08",
                "rows": [{"sensitive_unknown_field": "do-not-echo"}],
            },
        )

    failure = captured.value.failure
    assert failure.code is ToolErrorCode.INVALID_REQUEST
    assert failure.details
    assert "do-not-echo" not in failure.model_dump_json()


def test_domain_execution_failure_is_wrapped_in_stable_tool_error() -> None:
    registry = build_analysis_tool_registry()

    with pytest.raises(ToolInvocationError) as captured:
        registry.invoke(
            "analyze_dimension",
            {
                "dimension": "product",
                "current_period": "2026-08",
                "rows": [
                    {
                        "period": "2026-07",
                        "dimension": "product",
                        "member": "A",
                        "revenue": "100",
                        "cogs": "60",
                    }
                ],
            },
        )

    assert captured.value.failure.code is ToolErrorCode.EXECUTION_FAILED
    assert captured.value.failure.tool == "analyze_dimension"
