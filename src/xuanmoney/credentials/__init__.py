"""Application-owned credential resolution boundary."""

from .contracts import (
    CredentialResolutionError,
    CredentialResolutionFailureCode,
    CredentialResolver,
    ProtectedSecret,
)

__all__ = [
    "CredentialResolutionError",
    "CredentialResolutionFailureCode",
    "CredentialResolver",
    "ProtectedSecret",
]
