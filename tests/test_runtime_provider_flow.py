from xuanmoney.model.adapter import EchoModelAdapter
from xuanmoney.model.schemas import ModelRequest


class FakeRuntime:
    def __init__(self, provider):
        self.provider = provider

    def run(self, request):
        plan = self.provider.complete(request)
        return self.provider.complete(plan)


def test_runtime_can_use_provider_contract():
    provider = EchoModelAdapter()
    runtime = FakeRuntime(provider)

    result = runtime.run(ModelRequest(prompt="analyze revenue"))

    assert result is not None
