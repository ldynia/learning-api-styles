from collections.abc import Sequence

from starlette.datastructures import Headers
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send


class WebSocketOriginValidatorMiddleware:

    def __init__(self, app: ASGIApp, allow_origins: Sequence[str] | None = None):
        self.app = app
        self.allow_origins = allow_origins

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """
        This middleware looks at the client's 'origin' header to allow the client to connect.
        The connection is rejected if the clients supply a origin header that is not in the allow_origins list,
        or if the list is not set.
        The "*" wildcard allows all clients to connect.

        Args:
            scope: The ASGI connection scope dictionary.
            receive: Awaitable callable to receive events.
            send: Awaitable callable to send events.

        Returns:
            Awaitable: The result of calling the next ASGI app or a 403 response if the origin is not allowed.
        """
        if scope["type"] == "websocket":
            if not self.allow_origins:
                response = self.response("Origin not allowed", status_code=403)
                return await response(scope, receive, send)

            if "*" in self.allow_origins:
                return await self.app(scope, receive, send)

            # Check if the origin is in the allowed origins
            headers = Headers(scope=scope)
            origin = headers.get("origin")
            for host in self.allow_origins:
                if host.startswith("*") and host[1:] in origin:
                    return await self.app(scope, receive, send)

                if host in origin:
                    return await self.app(scope, receive, send)

            response = self.response("Origin not allowed", status_code=403)
            return await response(scope, receive, send)

    def response(self, body: str, status_code: int):
        """
        Creates a plain text HTTP response with the given body and status code.

        Args:
            body: The content to include in the response body.
            status_code: The HTTP status code for the response.

        Returns:
            PlainTextResponse: A response object containing the specified body and status code.
        """
        return PlainTextResponse(body, status_code=status_code)


class WebSocketTrustedHostMiddleware:

    def __init__(self, app: ASGIApp, allowed_hosts: Sequence[str] | None = None):
        self.app = app
        self.allowed_hosts = allowed_hosts

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """
        This middleware looks at the client's 'host' header to allow the client to connect.
        The connection is rejected if the clients supply a hostname that is not in the allowed_hosts list,
        or if the list is not set.
        The * wildcard matches any Host header value, allowing the server to accept requests destined for any server.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive callable.
            send: The ASGI send callable.

        Returns:
            Awaitable: The result of calling the next ASGI app or a 403 response if the host is not allowed.
        """
        if scope["type"] == "websocket":
            if not self.allowed_hosts:
                response = self.response("Host not allowed", status_code=403)
                return await response(scope, receive, send)

            if "*" in self.allowed_hosts:
                return await self.app(scope, receive, send)

            # Check if the host is in the allowed hosts
            headers = Headers(scope=scope)
            for host in self.allowed_hosts:
                if host.startswith("*") and host[1:] in headers.get("host"):
                    return await self.app(scope, receive, send)

                if host in headers.get("host"):
                    return await self.app(scope, receive, send)

            response = self.response("Host not allowed", status_code=403)
            return await response(scope, receive, send)

    def response(self, body: str, status_code: int):
        """
        Creates a PlainTextResponse with the given body and HTTP status code.

        Args:
            body: The response body as a plain text string.
            status_code: The HTTP status code for the response.

        Returns:
            PlainTextResponse: A response object with the specified body and status code.
        """
        return PlainTextResponse(body, status_code=status_code)
