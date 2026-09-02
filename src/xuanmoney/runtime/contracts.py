from __future__ import annotations

from typing import Annotated, Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from xuanmoney.tools import ToolMetadata


class ToolCallPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["tool_call"] = "tool_call"
    tool: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class NoToolPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["no_tool"] = "no_tool"
    reason: str = Field(min_length=1)


PlannerDecision = Annotated[
    ToolCallPlan | NoToolPlan,
    Field(discriminator="kind"),
]


class PlanningRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    tools: list[ToolMetadata] = Field(min_length=1)


class SynthesisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    tool_result: dict[str, Any]


class SynthesisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
