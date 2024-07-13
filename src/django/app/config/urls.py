from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenBlacklistView as TokenRevokeView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView
from starlette.routing import Route
from starlette.routing import WebSocketRoute
from strawberry.django.views import AsyncGraphQLView

from config.constants import DEBUG
from config.constants import ENVIRONMENT
from core.api.atom.feed import CityAtomFeedView
from core.api.atom.feed_enriched import CityAtomFeedEnrichedView
from core.api.atom.views import WeatherForecastFeedListView
from core.api.eventsource.v1.endpoints import AlertStreamingEndpoint
from core.api.graphql.schema import schema
from core.api.rest.v1.views import CityListView
from core.api.rest.v1.views import CityView
from core.api.rest.v1.views import GeocodingView
from core.api.rest.v1.views import WeatherForecastListView
from core.api.rest.v1.views import WeatherHistoryListView
from core.api.rest.v1.views import WeatherSeedView
from core.api.webhook.v1.views import WebhookStandardView
from core.api.webhook.v2.views import WebhookCustomView
from core.api.webhook.v3.views import WebhookEchoView
from core.api.websocket.v1.endpoints import AlertEndpoint
from core.api.websocket.v1.endpoints import ChatEndpoint
from core.api.websocket.v1.endpoints import EchoEndpoint
from core.www import root_view
from core.www import sse_alert_view
from core.www import swagger_rest_schema_view
from core.www import swagger_ws_schema_view
from core.www import ws_alert_view
from core.www import ws_chat_view
from core.www import ws_echo_view


# Django endpoints
urlpatterns = [
    # Django"s CMS backend
    path("admin", admin.site.urls),

    # WWW URNs (Server-side Events and WebSockets)
    path("", root_view),
    path("sse/alert", sse_alert_view),
    path("websocket/alert", ws_alert_view),
    path("websocket/chat", ws_chat_view),
    path("websocket/echo", ws_echo_view),
    path("websocket/docs/schema/manual", swagger_ws_schema_view, name="openapi_ws_schema_manual"),

    # Atom Feeds
    path("forecast/<uuid:city_uuid>", WeatherForecastFeedListView.as_view(), name="city_forecast"),
    path("forecast/feed", CityAtomFeedView(), name="city_feed"),
    path("forecast/feed_enriched", CityAtomFeedEnrichedView(), name="city_feed_enriched"),

    # REST API URNs
    path("api/cities", CityListView.as_view()),
    path("api/cities/<uuid:uuid>", CityView.as_view()),
    path("api/forecasts", WeatherForecastListView.as_view()),
    path("api/geocoding", GeocodingView.as_view()),
    path("api/history", WeatherHistoryListView.as_view()),
    path("api/jwt/obtain", TokenObtainPairView.as_view()),
    path("api/jwt/refresh", TokenRefreshView.as_view()),
    path("api/jwt/revoke", TokenRevokeView.as_view()),
    path("api/jwt/verify", TokenVerifyView.as_view()),
    path("api/docs/v1", SpectacularSwaggerView.as_view(url_name="oas_manual")),
    path("api/docs/v1/schema/auto", SpectacularAPIView.as_view(), name="oas_auto"),
    path("api/docs/v1/schema/manual", swagger_rest_schema_view, name="oas_manual"),

    # GraphQL URNs API and GraphiQL
    path("graphql", AsyncGraphQLView.as_view(
        schema=schema, graphql_ide=False, allow_queries_via_get=False
    )),

    # Webhooks URNs
    path("webhook/v1/echo", WebhookStandardView.as_view()),
    path("webhook/v2/echo", WebhookCustomView.as_view()),
    path("webhook/v3/echo", WebhookEchoView.as_view()),
]

if ENVIRONMENT == "development":
    urlpatterns += [path("api/seed", WeatherSeedView.as_view())]
    urlpatterns += [path("graphiql", csrf_exempt(AsyncGraphQLView.as_view(
        schema=schema, graphql_ide=True, allow_queries_via_get=False
    )))]

if DEBUG:
    urlpatterns += [path("debug/", include("debug_toolbar.urls"))]

# Starlette endpoints
routes = [
    WebSocketRoute("/ws/v1/alert", AlertEndpoint),
    WebSocketRoute("/ws/v1/chat", ChatEndpoint),
    WebSocketRoute("/ws/v1/echo", EchoEndpoint),
    Route("/sse/v1/alert", AlertStreamingEndpoint),
]
