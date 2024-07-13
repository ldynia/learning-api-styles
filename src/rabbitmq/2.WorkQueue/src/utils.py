import json

from typing import Any


def to_json(kwargs: dict) -> str:
    """
    Converts dictionary to json string.
    Args:
        kwargs (dict): Dictionary to convert.
    Returns:
        str: Json string.
    """
    return json.dumps(kwargs)


def json_to_dict(data: bytes, encoding="utf-8") -> dict:
    """
    Converts string to dictionary.
    Args:
        kwargs (bytes): Dictionary to convert.
    Returns:
        dict: decoded data.
    """
    return json.loads(data.decode(encoding))


def to_bool(value: Any) -> bool:
    """
    Converts a string to a boolean value.
    Args:
        value (Any): String to convert.
    Returns:
        bool: Boolean value.
    """
    BOOLEANS = {
        "true": True,
        "t": True,
        "yes": True,
        "y": True,
        "1": True,
        "false": False,
        "f": False,
        "no": False,
        "n": False,
        "0": False,
    }

    if isinstance(value, bool):
        return value

    if isinstance(value, bytes):
        value = value.decode("utf-8")

    value = value.strip().lower()
    if value in BOOLEANS:
        return BOOLEANS[value]

    return False
