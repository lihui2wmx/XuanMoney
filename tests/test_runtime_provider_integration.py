from xuanmoney.model.adapter import EchoModelAdapter
from xuanmoney.model.protocol import ModelProvider
from xuanmoney.model.schemas import ModelRequest


def test_echo_adapter_satisfies_provider_transport_contract():
    provider: ModelProvider = EchoModelAdapter()

    response = provider.complete(
        ModelRequest(
            prompt="summarize financial result",
            context={"query": "summarize financial result"},
        )
    )

    assert response.provider == "echo"
    assert response.content == "summarize financial result"


def test_provider_contract_does_not_claim_runtime_model_port_surface():
    provider = EchoModelAdapter()

    assert not hasattr(provider, "plan")
    assert not hasattr(provider, "synthesize")
    assert not hasattr(provider, "execute_tool")
    assert not hasattr(provider, "run_sql")
