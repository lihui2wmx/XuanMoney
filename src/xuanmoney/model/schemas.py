from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelRequest(BaseModel):
    """Input boundary for a model provider.

    Provider implementations must translate external payloads into this schema.
    """

    model_config = ConfigDict(extra="forbid")

    prompt: str
    context: dict[str, object] = Field(default_factory=dict)

    @field_validator("context")
    @classmethod
    def validate_context_is_json_safe(cls, value: dict[str, object]) -> dict[str, object]:
        return _validate_json_safe_mapping(value, field_name="context")


class ModelResponse(BaseModel):
    """Output boundary returned by a provider adapter."""

    model_config = ConfigDict(extra="forbid")

    content: str
    provider: str
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def validate_metadata_is_json_safe(cls, value: dict[str, object]) -> dict[str, object]:
        return _validate_json_safe_mapping(value, field_name="metadata")


def _validate_json_safe_mapping(
    value: dict[str, object], *, field_name: str
) -> dict[str, object]:
    """Reject non-JSON transport values without echoing their contents."""

    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must contain only JSON-safe values") from None
    return value
