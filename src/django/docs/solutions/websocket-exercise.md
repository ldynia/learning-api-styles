# Exercise 1

Extend our weather forecast service about chat application. In the chat, a user should be able to send and receive messages to and from a channel identified by a city's uuid identifier. In this exercise, you'll have to implement the chat's client and the server. The chat client is located at HTTP `http://localhost:8000/websocket/chat` endpoint and the server at WebSocket's `ws://localhost:8001/ws/v1/chat` endpoint. The second endpoint requires an authentication token to be passed as a *`token`* in the query parameter. To obtain the token, send a JSON encoded POST request to `http://localhost:8000/api/jwt/obtain` endpoint with the following payload *`username`* and *`password`* set to *`admin`*. When working with the WebSocket client, think about implementing a reconnecting mechanism in case of connection loss from the server side. When implementing the server, think about a mechanism that will broadcast messages to all connected on the channel clients.

## Solution

1. Add `websocket/chat` and `/ws/v1/chat` endpoint definition to the Django's project's `src/django/app/config/urls.py` file in `urlpatterns` and `routes` variables.
2. Add `/ws/v1/chat` to `APP_STARLETTE_AUTHENTICATE_ENDPOINTS` in the `src/django/app/config/constants.py` file.
3. Implement the chat client in the `src/django/app/core/www/templates/websocket/chat.html` and `src/django/app/core/www/static/app/js/chat.js` file.
4. Implement the chat server `ChatEndpoint` and add it to the `src/django/app/core/api/websocket/v1/endpoints.py` file.
