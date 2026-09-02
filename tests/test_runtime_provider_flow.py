from xuanmoney.model.adapter import EchoModelAdapter
from xuanmoney.model.schemas import ModelRequest


class FakeRuntime:
    def __init__(self, provider):
        self.provider = provider

    def run(self, request: ModelRequest):
        plan = self.provider.complete(request)
        synthesis_request = ModelRequest(
            prompt=plan.content,
            context={"previous_provider": plan.provider},
        )
        return self.provider.complete(synthesis_request)


def test_runtime_can_use_provider_contract():
    provider = EchoModelAdapter()
    runtime = FakeRuntime(provider)

    result = runtime.run(ModelRequest(prompt="analyze revenue"))

    assert result.content == "analyze revenue"
    assert result.provider == "echo"
