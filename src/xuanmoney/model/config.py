from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


_STRICT_MODEL = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CredentialSource(StrEnum):
    """Supported non-secret credential reference sources."""

    ENVIRONMENT = "environment"


class CredentialReference(BaseModel):
    """Reference a credential without carrying the credential value itself."""

    model_config = _STRICT_MODEL

    source: CredentialSource
    identifier: str = Field(min_length=1)


class ProviderConfiguration(BaseModel):
    """Provider-neutral configuration safe to serialize and inspect.

    Secret values are deliberately absent. Adapters may receive a
    CredentialReference and resolve it outside this contract in a later milestone.
    """

    model_config = _STRICT_MODEL

    provider_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    request_timeout_seconds: int = Field(default=30, ge=1, le=120)
    max_attempts: Literal[1] = 1
    credential_ref: CredentialReference | None = None
