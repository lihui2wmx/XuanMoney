from __future__ import annotations

import pytest

from xuanmoney.credentials import ProtectedSecret
from xuanmoney.model import (
    ModelRequest,
    ModelResponse,
    ProviderConfiguration,
    ProviderFailureCode,
    ProviderTransportError,
)
from xuanmoney.providers import ProviderFactoryRegistry


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


class InvalidFactory:
    pass


def configuration(provider_id: str) -> ProviderConfiguration:
    return ProviderConfiguration(provider_id=provider_id, model_id="fake-model")


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
