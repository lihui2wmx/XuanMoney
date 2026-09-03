from pydantic import ValidationError
import pytest

from xuanmoney.credentials import ProtectedSecret
from xuanmoney.model.schemas import ModelRequest, ModelResponse
from xuanmoney.model.protocol import ModelProvider


class FakeProvider(ModelProvider):
    def complete(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(content="ok", provider="fake")


def test_model_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ModelRequest(prompt="hello", unknown="blocked")


def test_model_response_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ModelResponse(content="ok", provider="fake", unknown="blocked")


def test_model_request_rejects_non_json_secret_context():
    with pytest.raises(ValidationError) as caught:
        ModelRequest(
            prompt="hello",
            context={"credential": ProtectedSecret("super-secret-value")},
        )

    assert "super-secret-value" not in str(caught.value)


def test_model_response_rejects_non_json_secret_metadata():
    with pytest.raises(ValidationError) as caught:
        ModelResponse(
            content="ok",
            provider="fake",
            metadata={"credential": ProtectedSecret("super-secret-value")},
        )

    assert "super-secret-value" not in str(caught.value)


def test_model_transport_rejects_non_standard_json_numbers():
    with pytest.raises(ValidationError):
        ModelRequest(prompt="hello", context={"value": float("nan")})

    with pytest.raises(ValidationError):
        ModelResponse(content="ok", provider="fake", metadata={"value": float("inf")})


def test_provider_contract_returns_response():
    provider = FakeProvider()
    result = provider.complete(ModelRequest(prompt="analyze"))
    assert result.content == "ok"
    assert result.provider == "fake"
