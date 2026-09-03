from __future__ import annotations

from types import MappingProxyType
from typing import Iterable, Mapping

from xuanmoney.credentials import CredentialResolver
from xuanmoney.model import (
    ModelProvider,
    ProviderConfiguration,
    ProviderFailureCode,
    ProviderTransportError,
)

from .composition import ProviderAdapterComposer, ProviderAdapterFactory


class ProviderFactoryRegistry:
    """Immutable application-owned allowlist of trusted provider factories.

    Provider selection is driven only by validated application configuration. The
    registry exposes no mutation or dynamic discovery surface.
    """

    __slots__ = ("_factories",)

    def __init__(
        self,
        entries: Iterable[tuple[str, ProviderAdapterFactory]],
    ) -> None:
        factories: dict[str, ProviderAdapterFactory] = {}
        for provider_id, factory in entries:
            normalized_id = _validate_provider_id(provider_id)
            if normalized_id in factories:
                raise ProviderTransportError(
                    ProviderFailureCode.INVALID_CONFIGURATION
                )
            if not callable(getattr(factory, "build", None)):
                raise ProviderTransportError(
                    ProviderFailureCode.INVALID_CONFIGURATION
                )
            factories[normalized_id] = factory

        self._factories: Mapping[str, ProviderAdapterFactory] = MappingProxyType(
            factories
        )

    def provider_ids(self) -> tuple[str, ...]:
        """Return the fixed provider identifiers in deterministic construction order."""

        return tuple(self._factories)

    def factory_for(
        self,
        configuration: ProviderConfiguration,
    ) -> ProviderAdapterFactory:
        """Select the trusted factory for application-owned provider configuration."""

        factory = self._factories.get(configuration.provider_id)
        if factory is None:
            raise ProviderTransportError(ProviderFailureCode.INVALID_CONFIGURATION)
        return factory

    def build(
        self,
        *,
        configuration: ProviderConfiguration,
        resolver: CredentialResolver,
    ) -> ModelProvider:
        """Compose the configured provider through the existing credential boundary."""

        return ProviderAdapterComposer(
            resolver=resolver,
            factory=self.factory_for(configuration),
        ).build(configuration)

    def __repr__(self) -> str:
        return "ProviderFactoryRegistry(<fixed provider allowlist>)"


def _validate_provider_id(provider_id: object) -> str:
    if not isinstance(provider_id, str):
        raise ProviderTransportError(ProviderFailureCode.INVALID_CONFIGURATION)
    normalized_id = provider_id.strip()
    if not normalized_id:
        raise ProviderTransportError(ProviderFailureCode.INVALID_CONFIGURATION)
    return normalized_id
