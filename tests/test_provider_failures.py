import json

import pytest
from pydantic import ValidationError

from xuanmoney.model import (
    ProviderFailure,
    ProviderFailureCode,
    ProviderTransportError,
)


@pytest.mark.parametrize(
    ("code", "expected_message"),
    [
        (ProviderFailureCode.INVALID_CONFIGURATION, "provider configuration is invalid"),
        (ProviderFailureCode.CREDENTIAL_UNAVAILABLE, "provider credential is unavailable"),
        (ProviderFailureCode.AUTHENTICATION_FAILED, "provider authentication failed"),
        (ProviderFailureCode.TIMEOUT, "provider request timed out"),
        (ProviderFailureCode.RATE_LIMITED, "provider request was rate limited"),
        (ProviderFailureCode.SERVICE_UNAVAILABLE, "provider service is unavailable"),
        (ProviderFailureCode.INVALID_RESPONSE, "provider response is invalid"),
        (ProviderFailureCode.TRANSPORT_ERROR, "provider transport failed"),
    ],
)
def test_provider_failure_uses_stable_safe_message(code, expected_message):
    failure = ProviderFailure.from_code(code)

    assert failure.message == expected_message
    assert failure.model_dump(mode="json") == {
        "code": code.value,
        "message": expected_message,
    }


def test_provider_failure_rejects_message_or_diagnostic_injection():
    with pytest.raises(ValidationError):
        ProviderFailure(
            code=ProviderFailureCode.TRANSPORT_ERROR,
            message="api-key-value: upstream stack trace",
        )

    with pytest.raises(ValidationError):
        ProviderFailure(
            code=ProviderFailureCode.TRANSPORT_ERROR,
            diagnostic="api-key-value: upstream stack trace",
        )


def test_provider_failure_is_immutable_after_validation():
    failure = ProviderFailure.from_code(ProviderFailureCode.TIMEOUT)

    with pytest.raises(ValidationError):
        failure.code = ProviderFailureCode.TRANSPORT_ERROR


def test_provider_transport_error_exposes_only_sanitized_failure():
    error = ProviderTransportError(ProviderFailureCode.TIMEOUT)
    serialized = json.dumps(error.failure.model_dump(mode="json"))

    assert str(error) == "provider request timed out"
    assert "api-key" not in serialized.lower()
    assert "stack trace" not in serialized.lower()
