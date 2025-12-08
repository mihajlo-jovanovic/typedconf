import inspect
from typing import Any, Callable, Dict, get_type_hints


def python_type_to_json(py_type: Any) -> str:
    """
    Maps Python types to JSON schema.
    """
    if py_type == str:
        return "string"
    elif py_type == int:
        return "integer"
    elif py_type == float:
        return "number"
    elif py_type == bool:
        return "boolean"
    elif py_type == list or getattr(py_type, "__origin__", None) == list:
        return "array"
    elif py_type == dict or getattr(py_type, "__origin__", None) == dict:
        return "object"
    # Fallback for more complex types or None
    return "string"  # Default to string for unknown types


def generate_tool_schema(func: Callable) -> Dict[str, Any]:
    """
    Introspect a Python function to generate an OpenAI-compatible tool definition.
    This replaces the need to manually write JSON schemas.
    """
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    # Base structure
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__.strip()
            if func.__doc__
            else "No description provided.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    for param_name, param in sig.parameters.items():
        if param_name == "self" or param_name == "cls":
            continue

        # Determine type
        param_type = type_hints.get(param_name, str)  # Default to string
        json_type = python_type_to_json(param_type)

        schema["function"]["parameters"]["properties"][param_name] = {"type": json_type}

        # Determine if required (no default value = required)
        if param.default == inspect.Parameter.empty:
            schema["function"]["parameters"]["required"].append(param_name)

    return schema
