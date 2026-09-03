from __future__ import annotations

import json
from types import MappingProxyType

import pytest

from xuanmoney.credentials import EnvironmentCredentialResolver, ProtectedSecret
from xuanmoney.model import (
    CredentialReference,
    CredentialSource,
    ModelRequest,
    ModelResponse,
    ProviderConfiguration,
    ProviderFailureCode,
    ProviderTransportError,
)
from xuanmoney.providers import ProviderFactoryRegistry
from xuanmoney.runtime import BoundedModelRuntime, ModelPortProviderBridge, RuntimeStatus


_FAKE_SECRET = "registry-test-provider-secret"


class ResolverThatMustNotRun:
    def resolve(self, reference: object) -> ProtectedSecret:
        raise AssertionError("resolver should not be called")


class FakeProvider:
    def complete(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(content="{}", provider="fake")


class RecordingFactory:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls = 0
        self.configurations: list[ProviderConfiguration] = []

    def build(
        self,
        configuration: ProviderConfiguration,
        credential: ProtectedSecret | None,
    ) -> FakeProvider:
        self.calls += 1
        self.configurations.append(configuration)
        assert credential is None
        return FakeProvider()


class CredentialConsumingProvider:
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
        self.adapter: CredentialConsumingProvider | None = None

    def build(
        self,
        configuration: ProviderConfiguration,
        credential: ProtectedSecret | None,
    ) -> CredentialConsumingProvider:
        self.calls += 1
        assert configuration.provider_id == "credential-provider"
        if credential is None:
            raise RuntimeError("credential required")
        adapter = CredentialConsumingProvider(credential.reveal(), self._outputs)
        self.adapter = adapter
        return adapter


class InvalidFactory:
    pass


def configuration(provider_id: str) -> ProviderConfiguration:
    return ProviderConfiguration(provider_id=provider_id, model_id="fake-model")


def credential_configuration() -> ProviderConfiguration:
    return ProviderConfiguration(
        provider_id="credential-provider",
        model_id="fake-model",
        credential_ref=CredentialReference(
            source=CredentialSource.ENVIRONMENT,
            identifier="XUANMONEY_PROVIDER_API_KEY",
        ),
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


def test_registry_selects_only_configured_factory_and_composes_provider() -> None:
    first = RecordingFactory("first")
    second = RecordingFactory("second")
    registry = ProviderFactoryRegistry(
        [("first-provider", first), ("second-provider", second)]
    )

    provider = registry.build(
        configuration=configuration("second-provider"),
        resolver=ResolverThatMustNotRun(),
    )

    assert isinstance(provider, FakeProvider)
    assert registry.provider_ids() == ("first-provider", "second-provider")
    assert first.calls == 0
    assert second.calls == 1
    assert second.configurations == [configuration("second-provider")]


def test_registry_credential_consuming_path_reaches_runtime_without_secret_leak() -> None:
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
    registry = ProviderFactoryRegistry([("credential-provider", factory)])

    provider = registry.build(
        configuration=credential_configuration(),
        resolver=resolver,
    )
    result = BoundedModelRuntime(
        model=ModelPortProviderBridge(provider=provider)
    ).run("How did profitability change?")

    assert result.status is RuntimeStatus.COMPLETE
    assert factory.calls == 1
    assert factory.adapter is provider
    assert factory.adapter is not None
    assert factory.adapter.credential_consumed is True
    assert len(factory.adapter.requests) == 2
    assert _FAKE_SECRET not in repr(registry)
    assert _FAKE_SECRET not in repr(factory)
    assert _FAKE_SECRET not in repr(provider)
    assert _FAKE_SECRET not in result.model_dump_json()
    assert all(
        _FAKE_SECRET not in request.model_dump_json()
        for request in factory.adapter.requests
    )


def test_unknown_provider_fails_closed_before_any_factory_invocation() -> None:
    factory = RecordingFactory("known")
    registry = ProviderFactoryRegistry([("known-provider", factory)])

    with pytest.raises(ProviderTransportError) as caught:
        registry.build(
            configuration=configuration("unknown-provider"),
            resolver=ResolverThatMustNotRun(),
        )

    assert caught.value.failure.code is ProviderFailureCode.INVALID_CONFIGURATION
    assert factory.calls == 0
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


def test_duplicate_provider_ids_fail_closed_after_configuration_normalization() -> None:
    with pytest.raises(ProviderTransportError) as caught:
        ProviderFactoryRegistry(
            [
                ("fake-provider", RecordingFactory("first")),
                ("  fake-provider  ", RecordingFactory("second")),
            ]
        )

    assert caught.value.failure.code is ProviderFailureCode.INVALID_CONFIGURATION


@pytest.mark.parametrize("provider_id", ["", "   ", 123, None])
def test_invalid_registry_provider_ids_fail_closed(provider_id: object) -> None:
    with pytest.raises(ProviderTransportError) as caught:
        ProviderFactoryRegistry([(provider_id, RecordingFactory("factory"))])  # type: ignore[list-item]

    assert caught.value.failure.code is ProviderFailureCode.INVALID_CONFIGURATION


def test_invalid_factory_fails_closed_at_registry_construction() -> None:
    with pytest.raises(ProviderTransportError) as caught:
        ProviderFactoryRegistry([("fake-provider", InvalidFactory())])  # type: ignore[list-item]

    assert caught.value.failure.code is ProviderFailureCode.INVALID_CONFIGURATION


def test_registry_is_snapshot_based_and_has_no_public_registration_surface() -> None:
    entries = [("first-provider", RecordingFactory("first"))]
    registry = ProviderFactoryRegistry(entries)
    entries.append(("second-provider", RecordingFactory("second")))

    assert registry.provider_ids() == ("first-provider",)
    assert not hasattr(registry, "register")
    assert "first-provider" not in repr(registry)
