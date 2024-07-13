# Helpers which are applicable across the whole project

import jwt

from typing import cast


def create_token_type(user: "AbstractBaseUser") -> "TokenType":
    """
    # Make JWT compatible between token generated from a REST API endpoint and GraphQL API
    """
    from gqlauth.core.utils import app_settings
    from gqlauth.jwt.types_ import TokenPayloadType, TokenType

    user_pk = app_settings.JWT_PAYLOAD_PK.python_name
    pk_field = {user_pk: getattr(user, user_pk)}
    payload = TokenPayloadType(**pk_field,)
    payload_dict = payload.as_dict()

    return TokenType(
        token=str(
            jwt.encode(
                payload=payload_dict,
                key=cast(str, app_settings.JWT_SECRET_KEY.value),
                algorithm=app_settings.JWT_ALGORITHM,
            )
        ),
        payload=payload,
    )


def to_boolean(value: str | bytes | bool):
    """Converts a string to a boolean value."""
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
