from __future__ import annotations

from typing import Protocol

from xuanmoney.credentials import (
    CredentialResolutionError,
    CredentialResolutionFailureCode,
    CredentialResolver,
    ProtectedSecret,
)
from xuanmoney.model import (
    ModelProvider,
    ProviderConfiguration,
    ProviderFailureCode,
    ProviderTransportError,
)


class ProviderAdapterFactory(Protocol):
    """Trusted provider-adapter construction boundary.

    Implementations may explicitly reveal ``ProtectedSecret`` only when constructing
    a provider client/adapter. They must not persist, log, serialize, or return the
    resolved value through model/runtime contracts.
    """

    def build(
        self,
        configuration: ProviderConfiguration,
        credential: ProtectedSecret | None,
    ) -> ModelProvider:
        ...


class ProviderAdapterComposer:
    """Resolve credentials and construct a provider adapter exactly once.

    The composer deliberately never reveals a ``ProtectedSecret``. A trusted factory
    owns the only permitted reveal point for client construction.
    """

    __slots__ = ("_resolver", "_factory")

    def __init__(
        self,
        *,
        resolver: CredentialResolver,
        factory: ProviderAdapterFactory,
    ) -> None:
        self._resolver = resolver
        self._factory = factory

    def build(self, configuration: ProviderConfiguration) -> ModelProvider:
        credential = self._resolve_credential(configuration)

        failure_code: ProviderFailureCode | None = None
        provider: ModelProvider | None = None
        try:
            provider = self._factory.build(configuration, credential)
        except ProviderTransportError as exc:
            failure_code = exc.failure.code
        except Exception:
            failure_code = ProviderFailureCode.TRANSPORT_ERROR

        if failure_code is not None:
            raise ProviderTransportError(failure_code)
        if provider is None:
            raise ProviderTransportError(ProviderFailureCode.TRANSPORT_ERROR)
        return provider

    def _resolve_credential(
        self,
        configuration: ProviderConfiguration,
    ) -> ProtectedSecret | None:
        reference = configuration.credential_ref
        if reference is None:
            return None

        failure_code: ProviderFailureCode | None = None
        credential: ProtectedSecret | None = None
        try:
            credential = self._resolver.resolve(reference)
        except CredentialResolutionError as exc:
            failure_code = _map_credential_failure(exc.code)
        except Exception:
            failure_code = ProviderFailureCode.CREDENTIAL_UNAVAILABLE

        if failure_code is not None:
            raise ProviderTransportError(failure_code)
        if not isinstance(credential, ProtectedSecret):
            raise ProviderTransportError(ProviderFailureCode.CREDENTIAL_UNAVAILABLE)
        return credential

    def __repr__(self) -> str:
        return "ProviderAdapterComposer(<protected composition boundary>)"


def _map_credential_failure(
    code: CredentialResolutionFailureCode,
) -> ProviderFailureCode:
    if code is CredentialResolutionFailureCode.UNSUPPORTED_SOURCE:
        return ProviderFailureCode.INVALID_CONFIGURATION
    return ProviderFailureCode.CREDENTIAL_UNAVAILABLE
