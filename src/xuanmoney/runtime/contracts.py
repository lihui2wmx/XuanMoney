from __future__ import annotations

from typing import Annotated, Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from xuanmoney.tools import ToolMetadata


_STRICT_MODEL = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ToolCallPlan(BaseModel):
    model_config = _STRICT_MODEL

    kind: Literal["tool_call"] = "tool_call"
    tool: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class NoToolPlan(BaseModel):
    model_config = _STRICT_MODEL

    kind: Literal["no_tool"] = "no_tool"
    reason: str = Field(min_length=1)


PlannerDecision = Annotated[
    ToolCallPlan | NoToolPlan,
    Field(discriminator="kind"),
]


class PlanningRequest(BaseModel):
    model_config = _STRICT_MODEL

    query: str = Field(min_length=1)
    tools: list[ToolMetadata] = Field(min_length=1)


class SynthesisRequest(BaseModel):
    model_config = _STRICT_MODEL

    query: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    tool_result: dict[str, Any]


class SynthesisOutput(BaseModel):
    model_config = _STRICT_MODEL

    answer: str = Field(min_length=1)


class ModelPort(Protocol):
    """Provider-independent structured model boundary.

    Implementations may call an external LLM later, but the runtime validates both
    planner and synthesis outputs. Returning `object` is intentional: provider adapters
    are untrusted at this boundary until their output passes Pydantic validation.
    """

    def plan(self, request: PlanningRequest) -> object:
        ...

    def synthesize(self, request: SynthesisRequest) -> object:
        ...
