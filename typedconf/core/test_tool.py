import pytest

from typedconf.core.tool import Tool


def sample_func(name: str, count: int = 1) -> str:
    """A sample function for testing."""
    return f"{name} " * count


def failing_func(x: int) -> int:
    """A function that raises an error."""
    raise ValueError("Intentional error")


class TestTool:
    def test_init_stores_func(self):
        tool = Tool(sample_func)
        assert tool.func is sample_func

    def test_init_generates_schema(self):
        tool = Tool(sample_func)
        assert tool.schema["type"] == "function"
        assert tool.schema["function"]["name"] == "sample_func"

    def test_execute_calls_function(self):
        tool = Tool(sample_func)
        result = tool.execute(name="hello", count=3)
        assert result == "hello hello hello "

    def test_execute_with_default_param(self):
        tool = Tool(sample_func)
        result = tool.execute(name="test")
        assert result == "test "

    def test_execute_returns_string(self):
        def returns_int(x: int) -> int:
            """Returns an int."""
            return x * 2

        tool = Tool(returns_int)
        result = tool.execute(x=5)
        assert result == "10"
        assert isinstance(result, str)

    def test_execute_handles_exception(self):
        tool = Tool(failing_func)
        result = tool.execute(x=1)
        assert "Error executing tool failing_func" in result
        assert "Intentional error" in result

    def test_to_openai_format_returns_schema(self):
        tool = Tool(sample_func)
        schema = tool.to_openai_format()
        assert schema == tool.schema
        assert schema["function"]["description"] == "A sample function for testing."

    def test_schema_has_correct_parameters(self):
        tool = Tool(sample_func)
        params = tool.schema["function"]["parameters"]
        assert params["properties"]["name"] == {"type": "string"}
        assert params["properties"]["count"] == {"type": "integer"}
        assert "name" in params["required"]
        assert "count" not in params["required"]
