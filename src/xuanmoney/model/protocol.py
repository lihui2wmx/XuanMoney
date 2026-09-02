from __future__ import annotations

from typing import Protocol

from .schemas import ModelRequest, ModelResponse


class ModelProvider(Protocol):
    """Minimal provider-neutral model boundary.

    Implementations only translate model I/O. Runtime policy remains outside.
    """

    def complete(self, request: ModelRequest) -> ModelResponse:
        """Generate a structured model response."""
        ...
