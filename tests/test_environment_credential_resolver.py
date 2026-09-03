from types import MappingProxyType

import pytest

from xuanmoney.credentials import (
    CredentialResolutionError,
    CredentialResolutionFailureCode,
    EnvironmentCredentialResolver,
    ProtectedSecret,
)
from xuanmoney.model import CredentialReference, CredentialSource


class FailingMapping(dict[str, str]):
    def get(self, key: str, default: object = None) -> object:
        raise RuntimeError("upstream diagnostic containing secret material")


def environment_reference(identifier: str = "XUANMONEY_PROVIDER_API_KEY") -> CredentialReference:
    return CredentialReference(
        source=CredentialSource.ENVIRONMENT,
        identifier=identifier,
    )


def test_environment_resolver_returns_protected_secret_from_read_only_mapping():
    values = MappingProxyType(
        {"XUANMONEY_PROVIDER_API_KEY": "super-secret-value"}
    )
    resolver = EnvironmentCredentialResolver(values)

    secret = resolver.resolve(environment_reference())

    assert isinstance(secret, ProtectedSecret)
    assert secret.reveal() == "super-secret-value"
    assert str(secret) == "<redacted>"
    assert "super-secret-value" not in repr(resolver)


def test_environment_resolver_missing_reference_is_sanitized():
    resolver = EnvironmentCredentialResolver(MappingProxyType({}))

    with pytest.raises(CredentialResolutionError) as caught:
        resolver.resolve(environment_reference("HIGHLY_SENSITIVE_REFERENCE_NAME"))

    error = caught.value
    assert error.code is CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE
    assert str(error) == "credential is unavailable"
    assert "HIGHLY_SENSITIVE_REFERENCE_NAME" not in str(error)
    assert "HIGHLY_SENSITIVE_REFERENCE_NAME" not in repr(error)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_environment_resolver_rejects_empty_value_without_exposing_reference():
    resolver = EnvironmentCredentialResolver(
        MappingProxyType({"EMPTY_PROVIDER_KEY": ""})
    )

    with pytest.raises(CredentialResolutionError) as caught:
        resolver.resolve(environment_reference("EMPTY_PROVIDER_KEY"))

    error = caught.value
    assert error.code is CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE
    assert "EMPTY_PROVIDER_KEY" not in str(error)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_environment_resolver_rejects_non_string_value_fail_closed():
    values: dict[str, object] = {"INVALID_PROVIDER_KEY": object()}
    resolver = EnvironmentCredentialResolver(values)  # type: ignore[arg-type]

    with pytest.raises(CredentialResolutionError) as caught:
        resolver.resolve(environment_reference("INVALID_PROVIDER_KEY"))

    error = caught.value
    assert error.code is CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE
    assert "INVALID_PROVIDER_KEY" not in str(error)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_environment_resolver_rejects_unsupported_source_fail_closed():
    reference = CredentialReference.model_construct(
        source="future-secret-manager",
        identifier="FUTURE_REFERENCE",
    )
    resolver = EnvironmentCredentialResolver(MappingProxyType({}))

    with pytest.raises(CredentialResolutionError) as caught:
        resolver.resolve(reference)

    error = caught.value
    assert error.code is CredentialResolutionFailureCode.UNSUPPORTED_SOURCE
    assert str(error) == "credential source is unsupported"
    assert "FUTURE_REFERENCE" not in str(error)


def test_environment_resolver_sanitizes_mapping_lookup_failures():
    resolver = EnvironmentCredentialResolver(FailingMapping())

    with pytest.raises(CredentialResolutionError) as caught:
        resolver.resolve(environment_reference("SENSITIVE_REFERENCE"))

    error = caught.value
    assert error.code is CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE
    assert str(error) == "credential is unavailable"
    assert "upstream diagnostic" not in str(error)
    assert "SENSITIVE_REFERENCE" not in str(error)
    assert error.__cause__ is None
    assert error.__context__ is None
