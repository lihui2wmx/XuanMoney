from __future__ import annotations

import json
from types import MappingProxyType

import pytest

from xuanmoney.credentials import (
    CredentialResolutionError,
    CredentialResolutionFailureCode,
    EnvironmentCredentialResolver,
    ProtectedSecret,
)
from xuanmoney.model import (
    CredentialReference,
    CredentialSource,
    ModelRequest,
    ModelResponse,
    ProviderConfiguration,
    ProviderFailureCode,
    ProviderTransportError,
)
from xuanmoney.providers import ProviderAdapterComposer
from xuanmoney.runtime import BoundedModelRuntime, ModelPortProviderBridge, RuntimeStatus


_FAKE_SECRET = "test-provider-secret-value"


class CredentialConsumingFakeAdapter:
    def __init__(self, credential_value: str, outputs: list[ModelResponse]) -> None:
        if credential_value != _FAKE_SECRET:
            raise RuntimeError("credential rejected")
        self.credential_consumed = True
        self._outputs = list(outputs)
        self.requests: list[ModelRequest] = []

    def complete(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        return self._outputs.pop(0)


class CredentialConsumingFactory:
    def __init__(self, outputs: list[ModelResponse]) -> None:
        self._outputs = list(outputs)
        self.calls = 0
        self.credential_consumed = False
        self.adapter: CredentialConsumingFakeAdapter | None = None

    def build(
        self,
        configuration: ProviderConfiguration,
        credential: ProtectedSecret | None,
    ) -> CredentialConsumingFakeAdapter:
        self.calls += 1
        assert configuration.provider_id == "fake-provider"
        if credential is None:
            raise RuntimeError("credential required")

        # This factory is the trusted client-construction boundary. The raw value is
        # used only as a constructor argument and is never stored on the factory.
        adapter = CredentialConsumingFakeAdapter(credential.reveal(), self._outputs)
        self.credential_consumed = adapter.credential_consumed
        self.adapter = adapter
        return adapter


class RecordingFactory:
    def __init__(self) -> None:
        self.calls = 0
        self.last_credential: ProtectedSecret | None = None

    def build(
        self,
        configuration: ProviderConfiguration,
        credential: ProtectedSecret | None,
    ) -> CredentialConsumingFakeAdapter:
        self.calls += 1
        self.last_credential = credential
        return CredentialConsumingFakeAdapter(_FAKE_SECRET, [])


class UnsupportedResolver:
    def resolve(self, reference: CredentialReference) -> ProtectedSecret:
        raise CredentialResolutionError(
            CredentialResolutionFailureCode.UNSUPPORTED_SOURCE
        )


class InvalidResolver:
    def resolve(self, reference: CredentialReference) -> object:
        return "raw-secret-value"


class SecretBearingFailureFactory:
    def build(
        self,
        configuration: ProviderConfiguration,
        credential: ProtectedSecret | None,
    ) -> CredentialConsumingFakeAdapter:
        assert credential is not None
        value = credential.reveal()
        raise RuntimeError(f"client construction failed with {value}")


def provider_configuration(*, with_credential: bool = True) -> ProviderConfiguration:
    reference = None
    if with_credential:
        reference = CredentialReference(
            source=CredentialSource.ENVIRONMENT,
            identifier="XUANMONEY_PROVIDER_API_KEY",
        )
    return ProviderConfiguration(
        provider_id="fake-provider",
        model_id="fake-model",
        credential_ref=reference,
    )


def financial_plan() -> dict[str, object]:
    return {
        "kind": "tool_call",
        "tool": "analyze_financials",
        "arguments": {
            "query": "compare profitability",
            "current": {
                "period": "2026-08",
                "revenue": "1000",
                "cogs": "600",
                "operating_expenses": "100",
                "taxes": "20",
            },
            "previous": {
                "period": "2026-07",
                "revenue": "900",
                "cogs": "550",
                "operating_expenses": "90",
                "taxes": "18",
            },
        },
    }


def test_composed_provider_consumes_credential_without_transport_or_runtime_leak() -> None:
    resolver = EnvironmentCredentialResolver(
        MappingProxyType({"XUANMONEY_PROVIDER_API_KEY": _FAKE_SECRET})
    )
    factory = CredentialConsumingFactory(
        outputs=[
            ModelResponse(content=json.dumps(financial_plan()), provider="fake"),
            ModelResponse(
                content=json.dumps({"answer": "Validated financial result."}),
                provider="fake",
            ),
        ]
    )
    composer = ProviderAdapterComposer(resolver=resolver, factory=factory)

    provider = composer.build(provider_configuration())
    result = BoundedModelRuntime(
        model=ModelPortProviderBridge(provider=provider)
    ).run("How did profitability change?")

    assert result.status is RuntimeStatus.COMPLETE
    assert factory.calls == 1
    assert factory.credential_consumed is True
    assert factory.adapter is provider
    assert factory.adapter is not None
    assert len(factory.adapter.requests) == 2
    assert _FAKE_SECRET not in result.model_dump_json()
    assert _FAKE_SECRET not in repr(composer)
    assert _FAKE_SECRET not in repr(factory)
    assert _FAKE_SECRET not in repr(provider)
    assert all(
        _FAKE_SECRET not in request.model_dump_json()
        for request in factory.adapter.requests
    )


def test_missing_credential_fails_before_factory_without_reference_leak() -> None:
    resolver = EnvironmentCredentialResolver(MappingProxyType({}))
    factory = RecordingFactory()
    composer = ProviderAdapterComposer(resolver=resolver, factory=factory)

    with pytest.raises(ProviderTransportError) as caught:
        composer.build(provider_configuration())

    error = caught.value
    assert error.failure.code is ProviderFailureCode.CREDENTIAL_UNAVAILABLE
    assert factory.calls == 0
    assert "XUANMONEY_PROVIDER_API_KEY" not in str(error)
    assert "XUANMONEY_PROVIDER_API_KEY" not in repr(error)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_unsupported_credential_source_maps_to_invalid_configuration() -> None:
    factory = RecordingFactory()
    composer = ProviderAdapterComposer(resolver=UnsupportedResolver(), factory=factory)

    with pytest.raises(ProviderTransportError) as caught:
        composer.build(provider_configuration())

    assert caught.value.failure.code is ProviderFailureCode.INVALID_CONFIGURATION
    assert factory.calls == 0
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


def test_invalid_resolver_return_type_fails_closed_before_factory() -> None:
    factory = RecordingFactory()
    composer = ProviderAdapterComposer(resolver=InvalidResolver(), factory=factory)

    with pytest.raises(ProviderTransportError) as caught:
        composer.build(provider_configuration())

    assert caught.value.failure.code is ProviderFailureCode.CREDENTIAL_UNAVAILABLE
    assert factory.calls == 0


def test_factory_failure_after_reveal_is_sanitized_without_exception_chain() -> None:
    resolver = EnvironmentCredentialResolver(
        MappingProxyType({"XUANMONEY_PROVIDER_API_KEY": _FAKE_SECRET})
    )
    composer = ProviderAdapterComposer(
        resolver=resolver,
        factory=SecretBearingFailureFactory(),
    )

    with pytest.raises(ProviderTransportError) as caught:
        composer.build(provider_configuration())

    error = caught.value
    assert error.failure.code is ProviderFailureCode.TRANSPORT_ERROR
    assert _FAKE_SECRET not in str(error)
    assert _FAKE_SECRET not in repr(error)
    assert error.__cause__ is None
    assert error.__context__ is None


def test_configuration_without_credential_skips_resolver() -> None:
    class ResolverThatMustNotRun:
        def resolve(self, reference: CredentialReference) -> ProtectedSecret:
            raise AssertionError("resolver should not be called")

    factory = RecordingFactory()
    composer = ProviderAdapterComposer(
        resolver=ResolverThatMustNotRun(),
        factory=factory,
    )

    provider = composer.build(provider_configuration(with_credential=False))

    assert provider is not None
    assert factory.calls == 1
    assert factory.last_credential is None
