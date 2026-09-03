from __future__ import annotations

from collections.abc import Mapping

from xuanmoney.model import CredentialReference, CredentialSource

from .contracts import (
    CredentialResolutionError,
    CredentialResolutionFailureCode,
    CredentialResolver,
    ProtectedSecret,
)


_MISSING = object()


class EnvironmentCredentialResolver(CredentialResolver):
    """Resolve environment credential references from an injected mapping.

    The resolver never imports or reads ``os.environ`` itself. Application composition
    may explicitly pass a read-only environment mapping while tests can inject a fully
    deterministic mapping.
    """

    __slots__ = ("__values",)

    def __init__(self, values: Mapping[str, str]) -> None:
        self.__values = values

    def __repr__(self) -> str:
        return "EnvironmentCredentialResolver(<redacted-mapping>)"

    def resolve(self, reference: CredentialReference) -> ProtectedSecret:
        if reference.source is not CredentialSource.ENVIRONMENT:
            raise CredentialResolutionError(
                CredentialResolutionFailureCode.UNSUPPORTED_SOURCE
            )

        lookup_failed = False
        value: object = _MISSING
        try:
            value = self.__values.get(reference.identifier, _MISSING)
        except Exception:
            lookup_failed = True

        if lookup_failed or value is _MISSING or not isinstance(value, str) or value == "":
            raise CredentialResolutionError(
                CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE
            )

        return ProtectedSecret(value)
