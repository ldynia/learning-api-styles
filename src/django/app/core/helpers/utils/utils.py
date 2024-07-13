import base64
import hashlib
import hmac

from typing import List, Any


def get_serializer_errors(serializer) -> List[str]:
    """
    Extracts and formats errors from a serializer"s errors dictionary.

    Args:
        serializer: A serializer instance.

    Returns:
        List[str]: A list of formatted error messages.
    """
    errors = []
    for field, errs in serializer.errors.items():
        for err in errs:
            err = str(err)
            if field != "non_field_errors":
                err = f"Parameter `{field}` - {str(err)}"
            errors.append(err)

    return errors


def to_bytes(text: str, encoding: str = "utf-8") -> bytes:
    """
    Converts a string to bytes using the specified encoding.

    Args:
        text (str): The input string to convert.
        encoding (str, optional): The encoding to use. Defaults to "utf-8".

    Returns:
        bytes: The bytes representation of the text string.
    """
    return bytes(text, encoding)


def to_str(text: bytes, encoding: str = "utf-8") -> bytes:
    """
    Converts bytes to string using the specified encoding.

    Args:
        text (bytes): The input string to convert.
        encoding (str, optional): The encoding to use. Defaults to "utf-8".

    Returns:
        string: The string representation of the text input.
    """
    return text.decode(encoding)


def to_default(value: Any, default: Any = None) -> Any:
    """
    Returns the input value if it"s truthy; otherwise, returns the default value.

    Args:
        value: The value to check.
        default: The default value to return if the input value is falsy. Defaults to None.

    Returns:
        Any: The input value if truthy, otherwise the default value.
    """
    if value:
        return value

    return default


def to_hmac(data: bytes | str, secret: bytes | str, algo=hashlib.sha256) -> str:
    """
    Returns (HMAC-SHA256) digest of the input data using the specified secret.

    Args:
        data (bytes, str): The input data to hash.
        secret (bytes, str): The secret to use for hashing.
        algo (hashlib, optional): The hashing algorithm to use. Defaults to hashlib.sha256.

    Returns:
        str: The HMAC-SHA256 digest of the input data.
    """
    if isinstance(data, str):
        data = to_bytes(data)

    if isinstance(secret, str):
        secret = to_bytes(secret)

    return hmac.new(secret, data, algo).hexdigest()
