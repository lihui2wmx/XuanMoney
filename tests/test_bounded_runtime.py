from __future__ import annotations

from dataclasses import dataclass, field

from xuanmoney.runtime import (
    BoundedModelRuntime,
    PlanningRequest,
    RuntimeFailureCode,
    RuntimeStatus,
    SynthesisRequest,
)
from xuanmoney.tools import ToolErrorCode


@dataclass
class FakeModel:
    plan_output: object
    synthesis_output: object = field(default_factory=lambda: {"answer": "done"})
    plan_error: Exception | None = None
    synthesis_error: Exception | None = None
    planning_requests: list[PlanningRequest] = field(default_factory=list)
    synthesis_requests: list[SynthesisRequest] = field(default_factory=list)

    def plan(self, request: PlanningRequest) -> object:
        self.planning_requests.append(request)
        if self.plan_error is not None:
            raise self.plan_error
        return self.plan_output

    def synthesize(self, request: SynthesisRequest) -> object:
        self.synthesis_requests.append(request)
        if self.synthesis_error is not None:
            raise self.synthesis_error
        return self.synthesis_output


def financial_plan() -> dict[str, object]:
    return {
        "kind": "tool_call",
        "tool": "analyze_financials",
        "arguments": {
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
    }


def test_runtime_performs_exactly_one_plan_tool_and_synthesis_step() -> None:
    model = FakeModel(
        plan_output=financial_plan(),
        synthesis_output={"answer": "Profitability improved on the validated comparison."},
    )
    runtime = BoundedModelRuntime(model=model)

    result = runtime.run("How did profitability change?")

    assert result.status is RuntimeStatus.COMPLETE
    assert result.answer == "Profitability improved on the validated comparison."
    assert result.tool_result is not None
    assert result.tool_result["phase"] == "complete"
    assert len(model.planning_requests) == 1
    assert len(model.synthesis_requests) == 1

    offered = model.planning_requests[0].tools
    assert [item.name for item in offered] == ["analyze_financials", "analyze_dimension"]
    assert all(item.risk.value == "read_only" for item in offered)
    assert "load_income_statements" not in {item.name for item in offered}

    synthesis_request = model.synthesis_requests[0]
    assert synthesis_request.query == "How did profitability change?"
    assert synthesis_request.tool_name == "analyze_financials"
    assert synthesis_request.tool_result == result.tool_result


def test_no_tool_plan_terminates_without_synthesis() -> None:
    model = FakeModel(
        plan_output={
            "kind": "no_tool",
            "reason": "No registered deterministic tool can answer this request.",
        }
    )

    result = BoundedModelRuntime(model=model).run("Predict the stock price tomorrow")

    assert result.status is RuntimeStatus.NO_TOOL
    assert result.answer is None
    assert result.planner_reason == "No registered deterministic tool can answer this request."
    assert len(model.planning_requests) == 1
    assert model.synthesis_requests == []


def test_whitespace_only_no_tool_reason_is_invalid() -> None:
    model = FakeModel(plan_output={"kind": "no_tool", "reason": "   "})

    result = BoundedModelRuntime(model=model).run("Unsupported request")

    assert result.status is RuntimeStatus.PLANNER_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.INVALID_PLAN
    assert model.synthesis_requests == []


def test_unknown_tool_from_planner_fails_closed_without_synthesis() -> None:
    model = FakeModel(
        plan_output={
            "kind": "tool_call",
            "tool": "python",
            "arguments": {"code": "print('bypass')"},
        }
    )

    result = BoundedModelRuntime(model=model).run("Run arbitrary code")

    assert result.status is RuntimeStatus.TOOL_FAILED
    assert result.tool_failure is not None
    assert result.tool_failure.code is ToolErrorCode.UNKNOWN_TOOL
    assert result.tool_failure.tool == "python"
    assert model.synthesis_requests == []


def test_invalid_tool_arguments_fail_without_retry_or_synthesis() -> None:
    model = FakeModel(
        plan_output={
            "kind": "tool_call",
            "tool": "analyze_dimension",
            "arguments": {
                "dimension": "product",
                "current_period": "2026-08",
                "rows": [],
            },
        }
    )

    result = BoundedModelRuntime(model=model).run("Analyze product performance")

    assert result.status is RuntimeStatus.TOOL_FAILED
    assert result.tool_failure is not None
    assert result.tool_failure.code is ToolErrorCode.INVALID_REQUEST
    assert len(model.planning_requests) == 1
    assert model.synthesis_requests == []


def test_tool_execution_failure_terminates_without_autonomous_fallback() -> None:
    model = FakeModel(
        plan_output={
            "kind": "tool_call",
            "tool": "analyze_dimension",
            "arguments": {
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
        }
    )

    result = BoundedModelRuntime(model=model).run("Analyze product performance")

    assert result.status is RuntimeStatus.TOOL_FAILED
    assert result.tool_failure is not None
    assert result.tool_failure.code is ToolErrorCode.EXECUTION_FAILED
    assert len(model.planning_requests) == 1
    assert model.synthesis_requests == []


def test_invalid_planner_output_never_reaches_tool_or_synthesis() -> None:
    model = FakeModel(
        plan_output={
            "kind": "tool_call",
            "tool": "analyze_financials",
            "arguments": {},
            "unexpected": "not allowed",
        }
    )

    result = BoundedModelRuntime(model=model).run("Analyze finance")

    assert result.status is RuntimeStatus.PLANNER_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.INVALID_PLAN
    assert model.synthesis_requests == []


def test_planner_exception_terminates_run_without_echoing_provider_error() -> None:
    secret = "provider-secret-diagnostic"
    model = FakeModel(plan_output={}, plan_error=RuntimeError(secret))

    result = BoundedModelRuntime(model=model).run("Analyze finance")

    assert result.status is RuntimeStatus.PLANNER_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.PLANNER_EXCEPTION
    assert result.runtime_failure.message == "planner invocation failed"
    assert secret not in result.model_dump_json()
    assert model.synthesis_requests == []


def test_invalid_synthesis_is_rejected_without_retry() -> None:
    model = FakeModel(plan_output=financial_plan(), synthesis_output={"answer": ""})

    result = BoundedModelRuntime(model=model).run("How did profitability change?")

    assert result.status is RuntimeStatus.SYNTHESIS_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.INVALID_SYNTHESIS
    assert len(model.planning_requests) == 1
    assert len(model.synthesis_requests) == 1


def test_whitespace_only_synthesis_is_rejected() -> None:
    model = FakeModel(plan_output=financial_plan(), synthesis_output={"answer": "   "})

    result = BoundedModelRuntime(model=model).run("How did profitability change?")

    assert result.status is RuntimeStatus.SYNTHESIS_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.INVALID_SYNTHESIS
    assert len(model.planning_requests) == 1
    assert len(model.synthesis_requests) == 1


def test_synthesis_exception_is_not_retried_or_echoed() -> None:
    secret = "provider-secret-diagnostic"
    model = FakeModel(
        plan_output=financial_plan(),
        synthesis_error=RuntimeError(secret),
    )

    result = BoundedModelRuntime(model=model).run("How did profitability change?")

    assert result.status is RuntimeStatus.SYNTHESIS_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.SYNTHESIS_EXCEPTION
    assert result.runtime_failure.message == "synthesizer invocation failed"
    assert secret not in result.model_dump_json()
    assert len(model.planning_requests) == 1
    assert len(model.synthesis_requests) == 1
