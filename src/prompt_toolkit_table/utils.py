"""Define helpers."""

from typing import Any


def _is_list_of_lists(data: Any) -> bool:
    """Check if data is a list of strings."""
    if data and isinstance(data, list):
        return all(isinstance(elem, list) for elem in data)
    else:
        return False


def _is_list_of_dictionaries(data: Any) -> bool:
    """Check if data is a list of dictionaries."""
    if data and isinstance(data, list):
        return all(isinstance(elem, dict) for elem in data)
    else:
        return False


def _is_list_of_pydantic(data: Any) -> bool:
    """Check if data is a list of pydantic objects."""
    if data and isinstance(data, list):
        return all(str(type(elem)) == "BaseModel" for elem in data)
    else:
        return False
