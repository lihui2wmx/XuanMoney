from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from xuanmoney.agent.state import FinanceAgentState
from xuanmoney.domain import (
    BalanceSheet,
    DimensionalAnalysisResult,
    DimensionalRow,
    IncomeStatement,
)
from xuanmoney.service import analyze_dimension, analyze_financials


class ToolRisk(StrEnum):
    READ_ONLY = "read_only"


class ToolErrorCode(StrEnum):
    UNKNOWN_TOOL = "unknown_tool"
    INVALID_REQUEST = "invalid_request"
    EXECUTION_FAILED = "execution_failed"
    INVALID_RESPONSE = "invalid_response"


class ToolFailure(BaseModel):
    code: ToolErrorCode
    tool: str
    message: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class ToolInvocationError(RuntimeError):
    """Stable error boundary for future model/tool adapters."""

    def __init__(self, failure: ToolFailure) -> None:
        self.failure = failure
        super().__init__(failure.message)


class AnalyzeFinancialsRequest(BaseModel):
    query: str
    current: IncomeStatement
    previous: IncomeStatement | None = None
    balance_sheet: BalanceSheet | None = None


class AnalyzeDimensionRequest(BaseModel):
    rows: list[DimensionalRow]
    dimension: str
    current_period: str
    previous_period: str | None = None


class ToolMetadata(BaseModel):
    name: str
    description: str
    risk: ToolRisk
    model_callable: bool
    request_schema: dict[str, Any]
    response_schema: dict[str, Any]


ToolHandler = Callable[[BaseModel], BaseModel]


@dataclass(frozen=True, slots=True)
class _ToolSpec:
    name: str
    description: str
    request_model: type[BaseModel]
    response_model: type[BaseModel]
    handler: ToolHandler
    risk: ToolRisk = ToolRisk.READ_ONLY
    model_callable: bool = True

    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            risk=self.risk,
            model_callable=self.model_callable,
            request_schema=self.request_model.model_json_schema(),
            response_schema=self.response_model.model_json_schema(),
        )


def _run_financial_analysis(request: BaseModel) -> BaseModel:
    typed = AnalyzeFinancialsRequest.model_validate(request)
    return analyze_financials(
        query=typed.query,
        current=typed.current,
        previous=typed.previous,
        balance_sheet=typed.balance_sheet,
    )


def _run_dimensional_analysis(request: BaseModel) -> BaseModel:
    typed = AnalyzeDimensionRequest.model_validate(request)
    return analyze_dimension(
        rows=typed.rows,
        dimension=typed.dimension,
        current_period=typed.current_period,
        previous_period=typed.previous_period,
    )


_DEFAULT_SPECS: tuple[_ToolSpec, ...] = (
    _ToolSpec(
        name="analyze_financials",
        description=(
            "Compute validated profitability metrics, period variance, and an exact "
            "profit bridge from normalized financial statements."
        ),
        request_model=AnalyzeFinancialsRequest,
        response_model=FinanceAgentState,
        handler=_run_financial_analysis,
    ),
    _ToolSpec(
        name="analyze_dimension",
        description=(
            "Aggregate and compare one explicitly named business dimension using "
            "normalized period/member revenue and COGS rows."
        ),
        request_model=AnalyzeDimensionRequest,
        response_model=DimensionalAnalysisResult,
        handler=_run_dimensional_analysis,
    ),
)


class AnalysisToolRegistry:
    """Immutable registry of explicitly approved read-only analysis operations.

    The registry intentionally has no public dynamic-registration API. A future LLM
    adapter can discover and invoke only the fixed operations assembled in code review.
    Filesystem loaders, SQL, Python execution, imports, and financial write actions are
    not part of the model-callable surface.
    """

    def __init__(self, specs: tuple[_ToolSpec, ...] = _DEFAULT_SPECS) -> None:
        by_name: dict[str, _ToolSpec] = {}
        for spec in specs:
            if spec.name in by_name:
                raise ValueError(f"duplicate tool name {spec.name!r}")
            if spec.risk is not ToolRisk.READ_ONLY:
                raise ValueError(
                    f"tool {spec.name!r} is not read-only and cannot enter this registry"
                )
            by_name[spec.name] = spec
        self._specs = MappingProxyType(by_name)

    def metadata(self, *, model_callable_only: bool = True) -> tuple[ToolMetadata, ...]:
        specs = self._specs.values()
        if model_callable_only:
            specs = (spec for spec in specs if spec.model_callable)
        return tuple(spec.metadata() for spec in specs)

    def names(self, *, model_callable_only: bool = True) -> tuple[str, ...]:
        return tuple(
            item.name for item in self.metadata(model_callable_only=model_callable_only)
        )

    def invoke(self, name: str, payload: Mapping[str, Any] | BaseModel) -> BaseModel:
        spec = self._specs.get(name)
        if spec is None or not spec.model_callable:
            raise ToolInvocationError(
                ToolFailure(
                    code=ToolErrorCode.UNKNOWN_TOOL,
                    tool=name,
                    message=f"tool {name!r} is not registered for model invocation",
                )
            )

        try:
            request = spec.request_model.model_validate(payload)
        except ValidationError as exc:
            raise ToolInvocationError(
                ToolFailure(
                    code=ToolErrorCode.INVALID_REQUEST,
                    tool=name,
                    message=f"request validation failed for tool {name!r}",
                    details=exc.errors(include_input=False, include_url=False),
                )
            ) from exc

        try:
            raw_result = spec.handler(request)
        except ToolInvocationError:
            raise
        except Exception as exc:
            raise ToolInvocationError(
                ToolFailure(
                    code=ToolErrorCode.EXECUTION_FAILED,
                    tool=name,
                    message=f"tool {name!r} execution failed: {exc}",
                )
            ) from exc

        try:
            return spec.response_model.model_validate(raw_result)
        except ValidationError as exc:
            raise ToolInvocationError(
                ToolFailure(
                    code=ToolErrorCode.INVALID_RESPONSE,
                    tool=name,
                    message=f"response validation failed for tool {name!r}",
                    details=exc.errors(include_input=False, include_url=False),
                )
            ) from exc


def build_analysis_tool_registry() -> AnalysisToolRegistry:
    return AnalysisToolRegistry()
