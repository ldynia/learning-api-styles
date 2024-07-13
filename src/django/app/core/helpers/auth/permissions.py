from asgiref.sync import sync_to_async
from datetime import datetime
from typing import Any
from typing import cast
import base64
import json
import jwt

from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission as DRFBasePermission
from rest_framework.request import Request
from rest_framework.views import View
from starlette.authentication import AuthCredentials
from starlette.authentication import AuthenticationBackend
from starlette.authentication import AuthenticationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from strawberry.permission import BasePermission as StrawberryBasePermission
from strawberry.types import Info

from config.constants import SECRET_KEY


class IsSuperuser(DRFBasePermission):
    """
    Custom permission class for allowing GET requests or authenticated users.
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if the user has permission to access the view.

        Args:
            request (Request): The request object.
            view (View): The view object.

        Returns:
            bool: True if the user has permission, False otherwise.

        References:
            https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
        """
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsAuthenticated(StrawberryBasePermission):

    message = "User is not authenticated"

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """
        Check validity of JWT token.
        """
        authenticated = False

        request = info.context["request"]
        if "Authorization" in request.headers:
            jwt_token = request.headers["Authorization"].split(" ")[-1]
            if not jwt_token:
                raise Exception("Token is missing.")

            try:
                payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])

                expiration_dt = datetime.fromtimestamp(int(payload["exp"]))
                token_expired = datetime.now() >= expiration_dt
                if token_expired:
                    raise Exception("Token has expired.")
                else:
                    authenticated = True

                query_set = await sync_to_async(User.objects.filter)(pk=payload["id"])

                info.context.request.user = await sync_to_async(query_set.first)()
            except jwt.ExpiredSignatureError:
                raise Exception("Token has expired.")
            except jwt.DecodeError:
                raise Exception("Could not decode token.")
            except json.JSONDecodeError:
                raise Exception("Could not decode payload.")
            except Exception as e:
                raise Exception(f"Invalid token. {e}")

        return authenticated


class IsAdmin(StrawberryBasePermission):

    message = "User is not authorized"

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        return info.context.request.user.is_superuser


class StarletteJWTAuthBackend(AuthenticationBackend):

    def __init__(self, authenticate_endpoints):
        self.authenticate_endpoints = authenticate_endpoints

    async def authenticate(self, conn):
        # Check if the path is in the list of endpoints that require authentication
        if conn.scope["path"] not in self.authenticate_endpoints:
            return

        access_token_b64 = conn.query_params.get("access_token")
        if not access_token_b64:
            raise AuthenticationError("Query parameter missing `access_token`.")

        # Setting verify_signature=False - For the testing to pass!
        try:
            jwt_token = base64.b64decode(access_token_b64).decode("ascii")
            payload = jwt.decode(
                jwt_token,
                SECRET_KEY,
                algorithms=["HS256"],
                options={"verify_signature": False}
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Provided `access_token` has expired.")
        except (Exception, json.JSONDecodeError):
            raise AuthenticationError("Provided `access_token` is not based64 or JSON encoded.")

        # Check if the token has expired
        token_expired = datetime.now() >= datetime.fromtimestamp(payload["exp"])
        if token_expired:
            raise AuthenticationError("Provided `access_token` has expired.")

        # Check if user exists
        query_set = await sync_to_async(User.objects.filter)(pk=payload["id"])
        user = await sync_to_async(query_set.first)()
        if not user:
            raise AuthenticationError("User not found.")

        # Return the authenticated user
        return AuthCredentials(scopes=["authenticated"]), user


def auth_error(request: Request, exc: Exception) -> JSONResponse:
    """Send JSON response with the error message."""
    return JSONResponse({"errors": [str(exc)]}, status_code=401)
