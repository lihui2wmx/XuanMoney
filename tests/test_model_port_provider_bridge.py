from __future__ import annotations

import json
from dataclasses import dataclass, field

from xuanmoney.model import ModelRequest, ModelResponse
from xuanmoney.runtime import (
    BoundedModelRuntime,
    ModelPortProviderBridge,
    PlanningRequest,
    RuntimeFailureCode,
    RuntimeStatus,
    SynthesisRequest,
)
from xuanmoney.tools import build_analysis_tool_registry


@dataclass
class FakeProvider:
    outputs: list[ModelResponse | Exception]
    requests: list[ModelRequest] = field(default_factory=list)

    def complete(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        output = self.outputs.pop(0)
        if isinstance(output, Exception):
            raise output
        return output


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


def test_bridge_translates_planning_request_to_provider_transport() -> None:
    provider = FakeProvider(
        outputs=[
            ModelResponse(
                content=json.dumps(
                    {
                        "kind": "no_tool",
                        "reason": "No registered tool applies.",
                    }
                ),
                provider="fake",
            )
        ]
    )
    bridge = ModelPortProviderBridge(provider=provider)
    request = PlanningRequest(
        query="Unsupported request",
        tools=list(build_analysis_tool_registry().metadata()),
    )

    result = bridge.plan(request)

    assert result == {
        "kind": "no_tool",
        "reason": "No registered tool applies.",
    }
    assert len(provider.requests) == 1
    transport = provider.requests[0]
    assert transport.context["phase"] == "planning"
    payload = transport.context["request"]
    assert isinstance(payload, dict)
    assert payload["query"] == "Unsupported request"
    assert [tool["name"] for tool in payload["tools"]] == [
        "analyze_financials",
        "analyze_dimension",
    ]
    assert isinstance(transport.context["response_schema"], dict)


def test_bridge_translates_synthesis_request_to_provider_transport() -> None:
    provider = FakeProvider(
        outputs=[
            ModelResponse(
                content=json.dumps({"answer": "Validated result."}),
                provider="fake",
            )
        ]
    )
    bridge = ModelPortProviderBridge(provider=provider)
    request = SynthesisRequest(
        query="Summarize the result",
        tool_name="analyze_financials",
        tool_result={"phase": "complete"},
    )

    result = bridge.synthesize(request)

    assert result == {"answer": "Validated result."}
    assert len(provider.requests) == 1
    transport = provider.requests[0]
    assert transport.context["phase"] == "synthesis"
    payload = transport.context["request"]
    assert isinstance(payload, dict)
    assert payload == {
        "query": "Summarize the result",
        "tool_name": "analyze_financials",
        "tool_result": {"phase": "complete"},
    }
    assert isinstance(transport.context["response_schema"], dict)


def test_bounded_runtime_executes_through_provider_bridge() -> None:
    provider = FakeProvider(
        outputs=[
            ModelResponse(content=json.dumps(financial_plan()), provider="fake"),
            ModelResponse(
                content=json.dumps(
                    {"answer": "Profitability improved on the validated comparison."}
                ),
                provider="fake",
            ),
        ]
    )
    bridge = ModelPortProviderBridge(provider=provider)

    result = BoundedModelRuntime(model=bridge).run("How did profitability change?")

    assert result.status is RuntimeStatus.COMPLETE
    assert result.answer == "Profitability improved on the validated comparison."
    assert len(provider.requests) == 2
    assert [request.context["phase"] for request in provider.requests] == [
        "planning",
        "synthesis",
    ]


def test_runtime_still_owns_structured_plan_validation() -> None:
    invalid_plan = financial_plan() | {"unexpected": "blocked"}
    provider = FakeProvider(
        outputs=[
            ModelResponse(content=json.dumps(invalid_plan), provider="fake"),
        ]
    )

    result = BoundedModelRuntime(
        model=ModelPortProviderBridge(provider=provider)
    ).run("Analyze finance")

    assert result.status is RuntimeStatus.PLANNER_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.INVALID_PLAN
    assert len(provider.requests) == 1


def test_invalid_provider_json_fails_without_retry() -> None:
    provider = FakeProvider(
        outputs=[ModelResponse(content="not-json", provider="fake")]
    )

    result = BoundedModelRuntime(
        model=ModelPortProviderBridge(provider=provider)
    ).run("Analyze finance")

    assert result.status is RuntimeStatus.PLANNER_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.PLANNER_EXCEPTION
    assert result.runtime_failure.message == "planner invocation failed"
    assert len(provider.requests) == 1


def test_provider_exception_is_sanitized_by_runtime() -> None:
    secret = "provider-secret-diagnostic"
    provider = FakeProvider(outputs=[RuntimeError(secret)])

    result = BoundedModelRuntime(
        model=ModelPortProviderBridge(provider=provider)
    ).run("Analyze finance")

    assert result.status is RuntimeStatus.PLANNER_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.PLANNER_EXCEPTION
    assert secret not in result.model_dump_json()
    assert len(provider.requests) == 1


def test_invalid_synthesis_json_fails_without_retry() -> None:
    provider = FakeProvider(
        outputs=[
            ModelResponse(content=json.dumps(financial_plan()), provider="fake"),
            ModelResponse(content="not-json", provider="fake"),
        ]
    )

    result = BoundedModelRuntime(
        model=ModelPortProviderBridge(provider=provider)
    ).run("How did profitability change?")

    assert result.status is RuntimeStatus.SYNTHESIS_FAILED
    assert result.runtime_failure is not None
    assert result.runtime_failure.code is RuntimeFailureCode.SYNTHESIS_EXCEPTION
    assert result.runtime_failure.message == "synthesizer invocation failed"
    assert len(provider.requests) == 2
