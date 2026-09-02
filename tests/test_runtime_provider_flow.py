from xuanmoney.model.adapter import EchoModelAdapter
from xuanmoney.model.schemas import ModelRequest


def test_provider_contract_supports_distinct_typed_requests():
    """Exercise provider transport only; this is not BoundedModelRuntime wiring."""

    provider = EchoModelAdapter()

    planning_transport = provider.complete(
        ModelRequest(
            prompt="plan analysis",
            context={"phase": "planning"},
        )
    )
    synthesis_transport = provider.complete(
        ModelRequest(
            prompt="synthesize analysis",
            context={
                "phase": "synthesis",
                "previous_provider": planning_transport.provider,
            },
        )
    )

    assert planning_transport.content == "plan analysis"
    assert synthesis_transport.content == "synthesize analysis"
    assert planning_transport.provider == synthesis_transport.provider == "echo"
