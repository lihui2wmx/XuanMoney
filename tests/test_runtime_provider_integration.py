from xuanmoney.model.adapter import EchoModelAdapter
from xuanmoney.model.schemas import ModelRequest
from xuanmoney.model.protocol import ModelProvider


def test_echo_adapter_satisfies_provider_contract():
    provider: ModelProvider = EchoModelAdapter()

    request = ModelRequest(
        task="analysis",
        input={"query": "summarize financial result"},
    )

    response = provider.complete(request)

    assert response.status == "ok"
    assert response.content is not None


def test_provider_contract_keeps_model_layer_separate():
    provider = EchoModelAdapter()

    assert not hasattr(provider, "execute_tool")
    assert not hasattr(provider, "run_sql")
