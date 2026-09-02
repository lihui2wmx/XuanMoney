from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from xuanmoney.runtime.contracts import (
    ModelPort,
    NoToolPlan,
    PlannerDecision,
    PlanningRequest,
    SynthesisOutput,
    SynthesisRequest,
    ToolCallPlan,
)
from xuanmoney.tools import (
    AnalysisToolRegistry,
    ToolFailure,
    ToolInvocationError,
    build_analysis_tool_registry,
)


class RuntimeStatus(StrEnum):
    COMPLETE = "complete"
    NO_TOOL = "no_tool"
    PLANNER_FAILED = "planner_failed"
    TOOL_FAILED = "tool_failed"
    SYNTHESIS_FAILED = "synthesis_failed"


class RuntimeFailureCode(StrEnum):
    PLANNER_EXCEPTION = "planner_exception"
    INVALID_PLAN = "invalid_plan"
    SYNTHESIS_EXCEPTION = "synthesis_exception"
    INVALID_SYNTHESIS = "invalid_synthesis"


class RuntimeFailure(BaseModel):
    code: RuntimeFailureCode
    message: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class RuntimeResult(BaseModel):
    query: str
    status: RuntimeStatus
    plan: ToolCallPlan | NoToolPlan | None = None
    tool_result: dict[str, Any] | None = None
    tool_failure: ToolFailure | None = None
    answer: str | None = None
    planner_reason: str | None = None
    runtime_failure: RuntimeFailure | None = None


_PLAN_ADAPTER = TypeAdapter(PlannerDecision)


class BoundedModelRuntime:
    """Execute at most one model-selected read-only analysis tool per user query.

    There is deliberately no retry loop and no ReAct-style autonomous continuation.
    A planner failure, tool failure, or synthesis failure terminates the run. The only
    executable operations are those exposed by the injected controlled tool registry.
    """

    def __init__(
        self,
        *,
        model: ModelPort,
        registry: AnalysisToolRegistry | None = None,
    ) -> None:
        self._model = model
        self._registry = registry or build_analysis_tool_registry()

    def run(self, query: str) -> RuntimeResult:
        try:
            planning_request = PlanningRequest(
                query=query,
                tools=list(self._registry.metadata()),
            )
        except ValidationError as exc:
            return RuntimeResult(
                query=query,
                status=RuntimeStatus.PLANNER_FAILED,
                runtime_failure=RuntimeFailure(
                    code=RuntimeFailureCode.INVALID_PLAN,
                    message="runtime planning request is invalid",
                    details=exc.errors(include_input=False, include_url=False),
                ),
            )

        try:
            raw_plan = self._model.plan(planning_request)
        except Exception:
            return RuntimeResult(
                query=query,
                status=RuntimeStatus.PLANNER_FAILED,
                runtime_failure=RuntimeFailure(
                    code=RuntimeFailureCode.PLANNER_EXCEPTION,
                    message="planner invocation failed",
                ),
            )

        try:
            plan = _PLAN_ADAPTER.validate_python(raw_plan)
        except ValidationError as exc:
            return RuntimeResult(
                query=query,
                status=RuntimeStatus.PLANNER_FAILED,
                runtime_failure=RuntimeFailure(
                    code=RuntimeFailureCode.INVALID_PLAN,
                    message="planner returned an invalid structured decision",
                    details=exc.errors(include_input=False, include_url=False),
                ),
            )

        if isinstance(plan, NoToolPlan):
            return RuntimeResult(
                query=query,
                status=RuntimeStatus.NO_TOOL,
                plan=plan,
                planner_reason=plan.reason,
            )

        try:
            tool_output = self._registry.invoke(plan.tool, plan.arguments)
        except ToolInvocationError as exc:
            return RuntimeResult(
                query=query,
                status=RuntimeStatus.TOOL_FAILED,
                plan=plan,
                tool_failure=exc.failure,
            )

        serialized_result = tool_output.model_dump(mode="json")
        synthesis_request = SynthesisRequest(
            query=query,
            tool_name=plan.tool,
            tool_result=serialized_result,
        )

        try:
            raw_synthesis = self._model.synthesize(synthesis_request)
        except Exception:
            return RuntimeResult(
                query=query,
                status=RuntimeStatus.SYNTHESIS_FAILED,
                plan=plan,
                tool_result=serialized_result,
                runtime_failure=RuntimeFailure(
                    code=RuntimeFailureCode.SYNTHESIS_EXCEPTION,
                    message="synthesizer invocation failed",
                ),
            )

        try:
            synthesis = SynthesisOutput.model_validate(raw_synthesis)
        except ValidationError as exc:
            return RuntimeResult(
                query=query,
                status=RuntimeStatus.SYNTHESIS_FAILED,
                plan=plan,
                tool_result=serialized_result,
                runtime_failure=RuntimeFailure(
                    code=RuntimeFailureCode.INVALID_SYNTHESIS,
                    message="synthesizer returned an invalid structured response",
                    details=exc.errors(include_input=False, include_url=False),
                ),
            )

        return RuntimeResult(
            query=query,
            status=RuntimeStatus.COMPLETE,
            plan=plan,
            tool_result=serialized_result,
            answer=synthesis.answer,
        )
