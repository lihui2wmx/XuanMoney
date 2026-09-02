from __future__ import annotations

from abc import ABC, abstractmethod

from .protocol import ModelProvider
from .schemas import ModelRequest, ModelResponse


class BaseModelAdapter(ModelProvider, ABC):
    """Provider implementation boundary.

    Concrete adapters may translate external model APIs here, but must not
    access finance tools or bypass the bounded runtime.
    """

    @abstractmethod
    def complete(self, request: ModelRequest) -> ModelResponse:
        raise NotImplementedError


class EchoModelAdapter(BaseModelAdapter):
    """Deterministic adapter used for local testing only."""

    def complete(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            content=request.prompt,
            provider="echo",
        )
