from __future__ import annotations

import json
from types import MappingProxyType, SimpleNamespace

import pytest

from xuanmoney.credentials import EnvironmentCredentialResolver, ProtectedSecret
from xuanmoney.model import (
    CredentialReference,
    CredentialSource,
    ModelRequest,
    ProviderConfiguration,
    ProviderFailureCode,
    ProviderTransportError,
)
from xuanmoney.providers import OpenAIProviderFactory, ProviderFactoryRegistry
from xuanmoney.runtime import BoundedModelRuntime, ModelPortProviderBridge, RuntimeStatus
import xuanmoney.providers.openai_adapter as adapter_module


_FAKE_SECRET = "openai-provider-test-secret"


class FakeResponses:
    def __init__(self, *, outputs: list[str] | None = None, error: Exception | None = None) -> None:
        self.outputs = list(outputs or [])
        self.error = error
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(dict(kwargs))
        if self.error is not None:
            raise self.error
        return SimpleNamespace(output_text=self.outputs.pop(0))


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


class InvalidClient:
    pass


def openai_configuration() -> ProviderConfiguration:
    return ProviderConfiguration(
        provider_id="openai",
        model_id="gpt-test",
        request_timeout_seconds=17,
        credential_ref=CredentialReference(
            source=CredentialSource.ENVIRONMENT,
            identifier="XUANMONEY_OPENAI_API_KEY",
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


def test_factory_reveals_credential_only_for_client_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = FakeResponses(outputs=["{\"ok\":true}"])
    client = FakeClient(responses)
    observed: dict[str, object] = {}

    def fake_build_openai_client(*, api_key: str, timeout: float, max_retries: int) -> object:
        observed["credential_matches"] = api_key == _FAKE_SECRET
        observed["timeout"] = timeout
        observed["max_retries"] = max_retries
        return client

    monkeypatch.setattr(adapter_module, "_build_openai_client", fake_build_openai_client)
    factory = OpenAIProviderFactory()
    provider = factory.build(openai_configuration(), ProtectedSecret(_FAKE_SECRET))

    assert observed == {
        "credential_matches": True,
        "timeout": 17.0,
        "max_retries": 0,
    }
    assert _FAKE_SECRET not in repr(factory)
    assert _FAKE_SECRET not in repr(provider)


def test_adapter_maps_existing_model_request_contract_to_one_responses_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = FakeResponses(outputs=["{\"answer\":\"ok\"}"])
    monkeypatch.setattr(
        adapter_module,
        "_build_openai_client",
        lambda **_: FakeClient(responses),
    )
    provider = OpenAIProviderFactory().build(
        openai_configuration(), ProtectedSecret(_FAKE_SECRET)
    )

    response = provider.complete(
        ModelRequest(
            prompt="Return JSON only.",
            context={"phase": "planning", "value": 3},
        )
    )

    assert response.content == "{\"answer\":\"ok\"}"
    assert response.provider == "openai"
    assert response.metadata == {}
    assert responses.calls == [
        {
            "model": "gpt-test",
            "instructions": "Return JSON only.",
            "input": '{"phase":"planning","value":3}',
        }
    ]
    assert "tools" not in responses.calls[0]
    assert "stream" not in responses.calls[0]
    assert "background" not in responses.calls[0]


def test_blank_response_text_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = FakeResponses(outputs=["   "])
    monkeypatch.setattr(
        adapter_module,
        "_build_openai_client",
        lambda **_: FakeClient(responses),
    )
    provider = OpenAIProviderFactory().build(
        openai_configuration(), ProtectedSecret(_FAKE_SECRET)
    )

    with pytest.raises(ProviderTransportError) as caught:
        provider.complete(ModelRequest(prompt="prompt", context={}))

    assert caught.value.failure.code is ProviderFailureCode.INVALID_RESPONSE
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None


@pytest.mark.parametrize(
    ("sdk_error_name", "expected_code"),
    [
        ("AuthenticationError", ProviderFailureCode.AUTHENTICATION_FAILED),
        ("PermissionDeniedError", ProviderFailureCode.AUTHENTICATION_FAILED),
        ("APITimeoutError", ProviderFailureCode.TIMEOUT),
        ("RateLimitError", ProviderFailureCode.RATE_LIMITED),
        ("InternalServerError", ProviderFailureCode.SERVICE_UNAVAILABLE),
        ("BadRequestError", ProviderFailureCode.INVALID_CONFIGURATION),
        ("NotFoundError", ProviderFailureCode.INVALID_CONFIGURATION),
        ("UnprocessableEntityError", ProviderFailureCode.INVALID_CONFIGURATION),
        ("APIConnectionError", ProviderFailureCode.TRANSPORT_ERROR),
    ],
)
def test_sdk_failures_normalize_without_diagnostic_or_secret_leak(
    monkeypatch: pytest.MonkeyPatch,
    sdk_error_name: str,
    expected_code: ProviderFailureCode,
) -> None:
    fake_error_type = type(f"Fake{sdk_error_name}", (Exception,), {})
    monkeypatch.setattr(adapter_module.openai, sdk_error_name, fake_error_type)
    diagnostic = f"raw provider diagnostic {_FAKE_SECRET}"
    responses = FakeResponses(error=fake_error_type(diagnostic))
    monkeypatch.setattr(
        adapter_module,
        "_build_openai_client",
        lambda **_: FakeClient(responses),
    )
    provider = OpenAIProviderFactory().build(
        openai_configuration(), ProtectedSecret(_FAKE_SECRET)
    )

    with pytest.raises(ProviderTransportError) as caught:
        provider.complete(ModelRequest(prompt="prompt", context={}))

    assert caught.value.failure.code is expected_code
    assert diagnostic not in str(caught.value)
    assert _FAKE_SECRET not in str(caught.value)
    assert _FAKE_SECRET not in caught.value.failure.model_dump_json()
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    assert len(responses.calls) == 1


def test_unexpected_sdk_failure_normalizes_to_transport_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    diagnostic = f"unexpected {_FAKE_SECRET}"
    responses = FakeResponses(error=RuntimeError(diagnostic))
    monkeypatch.setattr(
        adapter_module,
        "_build_openai_client",
        lambda **_: FakeClient(responses),
    )
    provider = OpenAIProviderFactory().build(
        openai_configuration(), ProtectedSecret(_FAKE_SECRET)
    )

    with pytest.raises(ProviderTransportError) as caught:
        provider.complete(ModelRequest(prompt="prompt", context={}))

    assert caught.value.failure.code is ProviderFailureCode.TRANSPORT_ERROR
    assert diagnostic not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    assert len(responses.calls) == 1


def test_factory_fails_closed_for_wrong_provider_or_missing_credential() -> None:
    factory = OpenAIProviderFactory()

    with pytest.raises(ProviderTransportError) as wrong_provider:
        factory.build(
            ProviderConfiguration(provider_id="other", model_id="gpt-test"),
            ProtectedSecret(_FAKE_SECRET),
        )
    assert wrong_provider.value.failure.code is ProviderFailureCode.INVALID_CONFIGURATION

    with pytest.raises(ProviderTransportError) as missing_credential:
        factory.build(
            ProviderConfiguration(provider_id="openai", model_id="gpt-test"),
            None,
        )
    assert missing_credential.value.failure.code is ProviderFailureCode.CREDENTIAL_UNAVAILABLE


def test_factory_rejects_invalid_sdk_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adapter_module, "_build_openai_client", lambda **_: InvalidClient())

    with pytest.raises(ProviderTransportError) as caught:
        OpenAIProviderFactory().build(
            openai_configuration(), ProtectedSecret(_FAKE_SECRET)
        )

    assert caught.value.failure.code is ProviderFailureCode.TRANSPORT_ERROR


def test_openai_registry_path_reaches_bounded_runtime_without_secret_leak(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = FakeResponses(
        outputs=[
            json.dumps(financial_plan()),
            json.dumps({"answer": "Validated financial result."}),
        ]
    )
    observed: dict[str, object] = {}

    def fake_build_openai_client(*, api_key: str, timeout: float, max_retries: int) -> object:
        observed["credential_matches"] = api_key == _FAKE_SECRET
        observed["timeout"] = timeout
        observed["max_retries"] = max_retries
        return FakeClient(responses)

    monkeypatch.setattr(adapter_module, "_build_openai_client", fake_build_openai_client)
    resolver = EnvironmentCredentialResolver(
        MappingProxyType({"XUANMONEY_OPENAI_API_KEY": _FAKE_SECRET})
    )
    registry = ProviderFactoryRegistry([("openai", OpenAIProviderFactory())])
    provider = registry.build(configuration=openai_configuration(), resolver=resolver)

    result = BoundedModelRuntime(
        model=ModelPortProviderBridge(provider=provider)
    ).run("How did profitability change?")

    assert result.status is RuntimeStatus.COMPLETE
    assert observed == {
        "credential_matches": True,
        "timeout": 17.0,
        "max_retries": 0,
    }
    assert len(responses.calls) == 2
    assert all(call["model"] == "gpt-test" for call in responses.calls)
    assert all("tools" not in call for call in responses.calls)
    assert all("stream" not in call for call in responses.calls)
    assert all("background" not in call for call in responses.calls)
    assert json.loads(str(responses.calls[0]["input"]))["phase"] == "planning"
    assert json.loads(str(responses.calls[1]["input"]))["phase"] == "synthesis"
    assert _FAKE_SECRET not in repr(registry)
    assert _FAKE_SECRET not in repr(provider)
    assert _FAKE_SECRET not in result.model_dump_json()
