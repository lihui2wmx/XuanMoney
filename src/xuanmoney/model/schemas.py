from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ModelRequest(BaseModel):
    """Input boundary for a model provider.

    Provider implementations must translate external payloads into this schema.
    """

    model_config = ConfigDict(extra="forbid")

    prompt: str
    context: dict[str, object] = {}


class ModelResponse(BaseModel):
    """Output boundary returned by a provider adapter."""

    model_config = ConfigDict(extra="forbid")

    content: str
    provider: str
    metadata: dict[str, object] = {}
