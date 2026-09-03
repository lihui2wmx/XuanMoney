from __future__ import annotations

import json
from typing import Any

import openai

from xuanmoney.credentials import ProtectedSecret
from xuanmoney.model import (
    ModelRequest,
    ModelResponse,
    ProviderConfiguration,
    ProviderFailureCode,
    ProviderTransportError,
)


_OPENAI_PROVIDER_ID = "openai"


class OpenAIProviderAdapter:
    """Translate the provider-neutral model contract to one Responses API call."""

    __slots__ = ("_client", "_model_id")

    def __init__(self, *, client: Any, model_id: str) -> None:
        self._client = client
        self._model_id = model_id

    def complete(self, request: ModelRequest) -> ModelResponse:
        failure_code: ProviderFailureCode | None = None
        response: object | None = None
        try:
            response = self._client.responses.create(
                model=self._model_id,
                instructions=request.prompt,
                input=json.dumps(
                    request.context,
                    allow_nan=False,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ),
            )
        except Exception as exc:
            failure_code = _map_openai_exception(exc)

        if failure_code is not None:
            raise ProviderTransportError(failure_code)

        content: object | None = None
        try:
            content = getattr(response, "output_text")
        except Exception:
            content = None

        if not isinstance(content, str) or not content.strip():
            raise ProviderTransportError(ProviderFailureCode.INVALID_RESPONSE)

        return ModelResponse(content=content, provider=_OPENAI_PROVIDER_ID)

    def __repr__(self) -> str:
        return "OpenAIProviderAdapter(<protected provider client>)"


class OpenAIProviderFactory:
    """Trusted OpenAI client-construction boundary.

    This factory is the only OpenAI-specific component permitted to reveal a
    ``ProtectedSecret``. The revealed value is passed directly into SDK client
    construction and is not persisted by the factory or adapter.
    """

    __slots__ = ()

    def build(
        self,
        configuration: ProviderConfiguration,
        credential: ProtectedSecret | None,
    ) -> OpenAIProviderAdapter:
        if configuration.provider_id != _OPENAI_PROVIDER_ID:
            raise ProviderTransportError(ProviderFailureCode.INVALID_CONFIGURATION)
        if credential is None:
            raise ProviderTransportError(ProviderFailureCode.CREDENTIAL_UNAVAILABLE)

        failure_code: ProviderFailureCode | None = None
        client: object | None = None
        try:
            client = _build_openai_client(
                api_key=credential.reveal(),
                timeout=float(configuration.request_timeout_seconds),
                max_retries=0,
            )
        except Exception as exc:
            failure_code = _map_openai_exception(exc)

        if failure_code is not None:
            raise ProviderTransportError(failure_code)
        if client is None or not callable(
            getattr(getattr(client, "responses", None), "create", None)
        ):
            raise ProviderTransportError(ProviderFailureCode.TRANSPORT_ERROR)

        return OpenAIProviderAdapter(client=client, model_id=configuration.model_id)

    def __repr__(self) -> str:
        return "OpenAIProviderFactory(<trusted client construction boundary>)"


def _build_openai_client(*, api_key: str, timeout: float, max_retries: int) -> object:
    return openai.OpenAI(
        api_key=api_key,
        timeout=timeout,
        max_retries=max_retries,
    )


def _map_openai_exception(exc: Exception) -> ProviderFailureCode:
    if isinstance(exc, (openai.AuthenticationError, openai.PermissionDeniedError)):
        return ProviderFailureCode.AUTHENTICATION_FAILED
    if isinstance(exc, openai.APITimeoutError):
        return ProviderFailureCode.TIMEOUT
    if isinstance(exc, openai.RateLimitError):
        return ProviderFailureCode.RATE_LIMITED
    if isinstance(exc, openai.InternalServerError):
        return ProviderFailureCode.SERVICE_UNAVAILABLE
    if isinstance(
        exc,
        (openai.BadRequestError, openai.NotFoundError, openai.UnprocessableEntityError),
    ):
        return ProviderFailureCode.INVALID_CONFIGURATION
    if isinstance(exc, openai.APIConnectionError):
        return ProviderFailureCode.TRANSPORT_ERROR
    if isinstance(exc, openai.APIStatusError):
        status_code = getattr(exc, "status_code", None)
        if status_code in (401, 403):
            return ProviderFailureCode.AUTHENTICATION_FAILED
        if status_code == 429:
            return ProviderFailureCode.RATE_LIMITED
        if isinstance(status_code, int) and status_code >= 500:
            return ProviderFailureCode.SERVICE_UNAVAILABLE
        if status_code in (400, 404, 422):
            return ProviderFailureCode.INVALID_CONFIGURATION
    return ProviderFailureCode.TRANSPORT_ERROR
