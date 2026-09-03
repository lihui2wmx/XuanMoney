import json
import pickle

import pytest

from xuanmoney.credentials import (
    CredentialResolutionError,
    CredentialResolutionFailureCode,
    CredentialResolver,
    ProtectedSecret,
)
from xuanmoney.model import CredentialReference, CredentialSource, ProviderConfiguration


class FakeCredentialResolver(CredentialResolver):
    def __init__(self, values: dict[str, str]) -> None:
        self._values = dict(values)

    def resolve(self, reference: CredentialReference) -> ProtectedSecret:
        if reference.source is not CredentialSource.ENVIRONMENT:
            raise CredentialResolutionError(
                CredentialResolutionFailureCode.UNSUPPORTED_SOURCE
            )
        if reference.identifier not in self._values:
            raise CredentialResolutionError(
                CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE
            )
        return ProtectedSecret(self._values[reference.identifier])


def test_resolver_returns_protected_secret_without_mutating_configuration():
    reference = CredentialReference(
        source=CredentialSource.ENVIRONMENT,
        identifier="XUANMONEY_PROVIDER_API_KEY",
    )
    config = ProviderConfiguration(
        provider_id="example-provider",
        model_id="example-model",
        credential_ref=reference,
    )
    resolver = FakeCredentialResolver(
        {"XUANMONEY_PROVIDER_API_KEY": "super-secret-value"}
    )

    secret = resolver.resolve(reference)
    serialized_config = json.dumps(config.model_dump(mode="json"))

    assert secret.reveal() == "super-secret-value"
    assert "super-secret-value" not in serialized_config
    assert config.credential_ref == reference


def test_protected_secret_redacts_textual_forms():
    secret = ProtectedSecret("super-secret-value")

    assert str(secret) == "<redacted>"
    assert repr(secret) == "ProtectedSecret(<redacted>)"
    assert f"{secret}" == "<redacted>"
    assert "super-secret-value" not in str(secret)
    assert "super-secret-value" not in repr(secret)


def test_protected_secret_rejects_common_serialization_paths():
    secret = ProtectedSecret("super-secret-value")

    with pytest.raises(TypeError):
        json.dumps({"credential": secret})

    with pytest.raises(TypeError):
        pickle.dumps(secret)


def test_protected_secret_is_immutable_and_rejects_empty_values():
    secret = ProtectedSecret("super-secret-value")

    with pytest.raises(AttributeError):
        secret.any_field = "replacement"

    with pytest.raises(ValueError):
        ProtectedSecret("")


def test_missing_credential_failure_is_sanitized_without_exception_chain():
    reference = CredentialReference(
        source=CredentialSource.ENVIRONMENT,
        identifier="HIGHLY_SENSITIVE_REFERENCE_NAME",
    )
    resolver = FakeCredentialResolver({})

    with pytest.raises(CredentialResolutionError) as caught:
        resolver.resolve(reference)

    error = caught.value
    assert error.code is CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE
    assert str(error) == "credential is unavailable"
    assert error.__cause__ is None
    assert error.__context__ is None
    assert "HIGHLY_SENSITIVE_REFERENCE_NAME" not in str(error)
    assert "HIGHLY_SENSITIVE_REFERENCE_NAME" not in repr(error)


def test_resolution_error_does_not_accept_reference_or_diagnostic_payloads():
    with pytest.raises(TypeError):
        CredentialResolutionError(
            CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE,
            reference="XUANMONEY_PROVIDER_API_KEY",
        )

    with pytest.raises(TypeError):
        CredentialResolutionError(
            CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE,
            diagnostic="upstream secret-bearing error",
        )
