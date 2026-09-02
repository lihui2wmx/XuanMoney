from xuanmoney.model.adapter import EchoModelAdapter
from xuanmoney.model.schemas import ModelRequest


def test_echo_adapter_implements_provider_boundary():
    adapter = EchoModelAdapter()
    result = adapter.complete(ModelRequest(prompt="hello"))

    assert result.content == "hello"
    assert result.provider == "echo"


def test_adapter_does_not_expand_runtime_surface():
    adapter = EchoModelAdapter()

    assert not hasattr(adapter, "execute_tool")
    assert not hasattr(adapter, "run_sql")
