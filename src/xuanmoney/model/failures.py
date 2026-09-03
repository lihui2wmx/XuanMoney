from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ProviderFailureCode(StrEnum):
    INVALID_CONFIGURATION = "invalid_configuration"
    CREDENTIAL_UNAVAILABLE = "credential_unavailable"
    AUTHENTICATION_FAILED = "authentication_failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_RESPONSE = "invalid_response"
    TRANSPORT_ERROR = "transport_error"


_SAFE_MESSAGES: dict[ProviderFailureCode, str] = {
    ProviderFailureCode.INVALID_CONFIGURATION: "provider configuration is invalid",
    ProviderFailureCode.CREDENTIAL_UNAVAILABLE: "provider credential is unavailable",
    ProviderFailureCode.AUTHENTICATION_FAILED: "provider authentication failed",
    ProviderFailureCode.TIMEOUT: "provider request timed out",
    ProviderFailureCode.RATE_LIMITED: "provider request was rate limited",
    ProviderFailureCode.SERVICE_UNAVAILABLE: "provider service is unavailable",
    ProviderFailureCode.INVALID_RESPONSE: "provider response is invalid",
    ProviderFailureCode.TRANSPORT_ERROR: "provider transport failed",
}


class ProviderFailure(BaseModel):
    """Public provider failure safe for serialization.

    Raw provider diagnostics, exception text, request payloads, and credentials are
    intentionally absent from this model.
    """

    model_config = ConfigDict(extra="forbid")

    code: ProviderFailureCode
    message: str

    @classmethod
    def from_code(cls, code: ProviderFailureCode) -> "ProviderFailure":
        return cls(code=code, message=_SAFE_MESSAGES[code])


class ProviderTransportError(RuntimeError):
    """Provider transport exception exposing only a sanitized failure contract."""

    def __init__(self, code: ProviderFailureCode) -> None:
        self.failure = ProviderFailure.from_code(code)
        super().__init__(self.failure.message)
