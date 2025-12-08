import inspect
from typing import Dict, List

import pytest

from typedconf.core.introspection import generate_tool_schema, python_type_to_json


class TestPythonTypeToJson:
    def test_str_returns_string(self):
        assert python_type_to_json(str) == "string"

    def test_int_returns_integer(self):
        assert python_type_to_json(int) == "integer"

    def test_float_returns_number(self):
        assert python_type_to_json(float) == "number"

    def test_bool_returns_boolean(self):
        assert python_type_to_json(bool) == "boolean"

    def test_list_returns_array(self):
        assert python_type_to_json(list) == "array"

    def test_generic_list_returns_array(self):
        assert python_type_to_json(List[str]) == "array"

    def test_dict_returns_object(self):
        assert python_type_to_json(dict) == "object"

    def test_generic_dict_returns_object(self):
        assert python_type_to_json(Dict[str, int]) == "object"

    def test_unknown_type_defaults_to_string(self):
        class CustomType:
            pass

        assert python_type_to_json(CustomType) == "string"

    def test_none_defaults_to_string(self):
        assert python_type_to_json(None) == "string"


class TestGenerateToolSchema:
    def test_basic_function_schema(self):
        def greet(name: str) -> str:
            """Greet a person by name."""
            return f"Hello, {name}"

        schema = generate_tool_schema(greet)

        assert schema["type"] == "function"
        assert schema["function"]["name"] == "greet"
        assert schema["function"]["description"] == "Greet a person by name."
        assert schema["function"]["parameters"]["properties"]["name"] == {"type": "string"}
        assert "name" in schema["function"]["parameters"]["required"]

    def test_function_without_docstring(self):
        def no_doc(x: int):
            pass

        schema = generate_tool_schema(no_doc)

        assert schema["function"]["description"] == "No description provided."

    def test_function_with_optional_param(self):
        def with_default(name: str, count: int = 5) -> str:
            """Function with optional parameter."""
            return name * count

        schema = generate_tool_schema(with_default)

        assert "name" in schema["function"]["parameters"]["required"]
        assert "count" not in schema["function"]["parameters"]["required"]
        assert schema["function"]["parameters"]["properties"]["count"] == {"type": "integer"}

    def test_function_with_multiple_types(self):
        def multi_type(text: str, count: int, ratio: float, flag: bool):
            """Function with multiple parameter types."""
            pass

        schema = generate_tool_schema(multi_type)

        props = schema["function"]["parameters"]["properties"]
        assert props["text"] == {"type": "string"}
        assert props["count"] == {"type": "integer"}
        assert props["ratio"] == {"type": "number"}
        assert props["flag"] == {"type": "boolean"}

    def test_function_with_list_param(self):
        def with_list(items: List[str]):
            """Function with list parameter."""
            pass

        schema = generate_tool_schema(with_list)

        assert schema["function"]["parameters"]["properties"]["items"] == {"type": "array"}

    def test_function_with_dict_param(self):
        def with_dict(data: Dict[str, int]):
            """Function with dict parameter."""
            pass

        schema = generate_tool_schema(with_dict)

        assert schema["function"]["parameters"]["properties"]["data"] == {"type": "object"}

    def test_function_without_type_hints_defaults_to_string(self):
        def untyped(name):
            """Function without type hints."""
            pass

        schema = generate_tool_schema(untyped)

        assert schema["function"]["parameters"]["properties"]["name"] == {"type": "string"}

    def test_method_skips_self_parameter(self):
        class MyClass:
            def method(self, value: int):
                """A method."""
                pass

        schema = generate_tool_schema(MyClass.method)

        assert "self" not in schema["function"]["parameters"]["properties"]
        assert "value" in schema["function"]["parameters"]["properties"]

    def test_classmethod_skips_cls_parameter(self):
        class MyClass:
            @classmethod
            def class_method(cls, value: str):
                """A class method."""
                pass

        schema = generate_tool_schema(MyClass.class_method)

        assert "cls" not in schema["function"]["parameters"]["properties"]
        assert "value" in schema["function"]["parameters"]["properties"]
