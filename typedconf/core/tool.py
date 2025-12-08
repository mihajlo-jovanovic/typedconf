from typing import Callable

from .introspection import generate_tool_schema


class Tool:
    """
    A wrapper class around a Python function that handles schema generation and execution.
    """

    def __init__(self, func: Callable):
        self.func = func
        self.schema = generate_tool_schema(func)

    def execute(self, **kwargs):
        """Executes the internal function with provided arguments."""
        try:
            return str(self.func(**kwargs))
        except Exception as e:
            return f"Error executing tool {self.func.__name__}: {str(e)}"

    def to_openai_format(self):
        return self.schema
