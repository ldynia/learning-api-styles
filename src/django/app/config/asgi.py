"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

application_django = get_asgi_application()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.base")

from config.base import DEBUG
from config.constants import APP_STARLETTE_AUTHENTICATE_ENDPOINTS
from config.urls import routes
from core.helpers.auth import auth_error
from core.helpers.auth import StarletteJWTAuthBackend
from core.helpers.middleware import WebSocketOriginValidatorMiddleware
from core.helpers.middleware import WebSocketTrustedHostMiddleware


middleware = [
    Middleware(WebSocketOriginValidatorMiddleware, allow_origins=["localhost:8000", "*-8000.app.github.dev"]),
    Middleware(WebSocketTrustedHostMiddleware, allowed_hosts=["localhost:8001", "*-8001.app.github.dev"]),
    Middleware(
        AuthenticationMiddleware,
        backend=StarletteJWTAuthBackend(APP_STARLETTE_AUTHENTICATE_ENDPOINTS),
        on_error=auth_error
    ),
]

application_starlette = Starlette(
    debug=DEBUG, routes=routes, middleware=middleware
)
