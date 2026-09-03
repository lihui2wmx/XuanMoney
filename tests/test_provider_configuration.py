import json

import pytest
from pydantic import ValidationError

from xuanmoney.model import (
    CredentialReference,
    CredentialSource,
    ProviderConfiguration,
)


def test_provider_configuration_is_non_secret_and_bounded():
    config = ProviderConfiguration(
        provider_id="example-provider",
        model_id="example-model",
        request_timeout_seconds=45,
        credential_ref=CredentialReference(
            source=CredentialSource.ENVIRONMENT,
            identifier="XUANMONEY_PROVIDER_API_KEY",
        ),
    )

    payload = config.model_dump(mode="json")
    serialized = json.dumps(payload)

    assert payload["provider_id"] == "example-provider"
    assert payload["model_id"] == "example-model"
    assert payload["request_timeout_seconds"] == 45
    assert payload["max_attempts"] == 1
    assert payload["credential_ref"] == {
        "source": "environment",
        "identifier": "XUANMONEY_PROVIDER_API_KEY",
    }
    assert "secret" not in serialized.lower()
    assert "api_key_value" not in serialized.lower()


def test_provider_configuration_rejects_blank_identifiers():
    with pytest.raises(ValidationError):
        ProviderConfiguration(provider_id="   ", model_id="model")

    with pytest.raises(ValidationError):
        ProviderConfiguration(provider_id="provider", model_id="   ")


def test_provider_configuration_rejects_unbounded_timeouts():
    with pytest.raises(ValidationError):
        ProviderConfiguration(
            provider_id="provider",
            model_id="model",
            request_timeout_seconds=0,
        )

    with pytest.raises(ValidationError):
        ProviderConfiguration(
            provider_id="provider",
            model_id="model",
            request_timeout_seconds=121,
        )


def test_provider_configuration_forbids_retry_expansion():
    with pytest.raises(ValidationError):
        ProviderConfiguration(
            provider_id="provider",
            model_id="model",
            max_attempts=2,
        )


def test_credential_reference_rejects_secret_material_fields():
    with pytest.raises(ValidationError):
        CredentialReference(
            source="environment",
            identifier="XUANMONEY_PROVIDER_API_KEY",
            secret="must-not-enter-contract",
        )

    with pytest.raises(ValidationError):
        ProviderConfiguration(
            provider_id="provider",
            model_id="model",
            api_key="must-not-enter-contract",
        )
