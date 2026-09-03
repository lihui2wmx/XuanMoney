from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from xuanmoney.model import CredentialReference


_REDACTED = "<redacted>"


class ProtectedSecret:
    """Opaque application-owned secret value.

    The value is intentionally excluded from repr/string forms and common
    serialization paths. Revealing the value is an explicit operation reserved for
    a future provider integration boundary.
    """

    __slots__ = ("__value", "__sealed")

    def __init__(self, value: str) -> None:
        if not isinstance(value, str) or not value:
            raise ValueError("protected secret must be a non-empty string")
        object.__setattr__(self, "_ProtectedSecret__value", value)
        object.__setattr__(self, "_ProtectedSecret__sealed", True)

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_ProtectedSecret__sealed", False):
            raise AttributeError("ProtectedSecret is immutable")
        object.__setattr__(self, name, value)

    def reveal(self) -> str:
        """Return the secret only at an explicitly trusted integration boundary."""

        return self.__value

    def __repr__(self) -> str:
        return f"ProtectedSecret({_REDACTED})"

    def __str__(self) -> str:
        return _REDACTED

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    def __reduce_ex__(self, protocol: int) -> object:
        raise TypeError("ProtectedSecret is not serializable")


class CredentialResolutionFailureCode(StrEnum):
    UNSUPPORTED_SOURCE = "unsupported_source"
    CREDENTIAL_UNAVAILABLE = "credential_unavailable"


_SAFE_MESSAGES: dict[CredentialResolutionFailureCode, str] = {
    CredentialResolutionFailureCode.UNSUPPORTED_SOURCE: "credential source is unsupported",
    CredentialResolutionFailureCode.CREDENTIAL_UNAVAILABLE: "credential is unavailable",
}


class CredentialResolutionError(RuntimeError):
    """Sanitized credential-resolution failure.

    The exception deliberately stores no credential reference, resolved value, or raw
    resolver diagnostic.
    """

    def __init__(self, code: CredentialResolutionFailureCode) -> None:
        self.code = code
        super().__init__(_SAFE_MESSAGES[code])


class CredentialResolver(Protocol):
    """Application-owned boundary for resolving non-secret credential references."""

    def resolve(self, reference: CredentialReference) -> ProtectedSecret:
        ...
