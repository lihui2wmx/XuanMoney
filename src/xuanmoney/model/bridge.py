from __future__ import annotations

import json

from pydantic import TypeAdapter

from xuanmoney.runtime.contracts import (
    PlannerDecision,
    PlanningRequest,
    SynthesisOutput,
    SynthesisRequest,
)

from .protocol import ModelProvider
from .schemas import ModelRequest


_PLANNER_SCHEMA = TypeAdapter(PlannerDecision).json_schema()
_SYNTHESIS_SCHEMA = SynthesisOutput.model_json_schema()


class ModelPortProviderBridge:
    """Implement the runtime-facing ModelPort over a lower-level ModelProvider.

    The bridge translates typed runtime requests into provider transport requests and
    decodes provider response content as JSON. It deliberately does not validate the
    decoded planning or synthesis objects: BoundedModelRuntime remains the owner of
    those validation and execution-policy decisions.
    """

    def __init__(self, *, provider: ModelProvider) -> None:
        self._provider = provider

    def plan(self, request: PlanningRequest) -> object:
        response = self._provider.complete(
            ModelRequest(
                prompt=(
                    "Return exactly one JSON planning decision for the supplied "
                    "XuanMoney planning request."
                ),
                context={
                    "phase": "planning",
                    "request": request.model_dump(mode="json"),
                    "response_schema": _PLANNER_SCHEMA,
                },
            )
        )
        return _decode_provider_content(response.content)

    def synthesize(self, request: SynthesisRequest) -> object:
        response = self._provider.complete(
            ModelRequest(
                prompt=(
                    "Return exactly one JSON synthesis object for the supplied "
                    "XuanMoney synthesis request."
                ),
                context={
                    "phase": "synthesis",
                    "request": request.model_dump(mode="json"),
                    "response_schema": _SYNTHESIS_SCHEMA,
                },
            )
        )
        return _decode_provider_content(response.content)


def _decode_provider_content(content: str) -> object:
    """Decode provider text without adding retries, fallback, or semantic validation."""

    return json.loads(content)
