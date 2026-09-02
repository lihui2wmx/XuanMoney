from pydantic import ValidationError
import pytest

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


def test_provider_contract_returns_response():
    provider = FakeProvider()
    result = provider.complete(ModelRequest(prompt="analyze"))
    assert result.content == "ok"
    assert result.provider == "fake"
