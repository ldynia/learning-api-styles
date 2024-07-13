import os

from django.shortcuts import render
from django.http import HttpResponse
from core.models import CityRepository

from config.base import logger
from config.constants import ENVIRONMENT
from config.constants import ASSETS_API_REST_SCHEMA
from config.constants import ASSETS_API_WS_SCHEMA


def root_view(request) -> HttpResponse:
    logger.info(f" {request.id} This is an info message.")
    city = CityRepository.get_first()
    return render(request, "index.html", {"city": city, "env": ENVIRONMENT})


def ws_echo_view(request) -> HttpResponse:
    return render(request, "websocket/echo.html")


def ws_chat_view(request) -> HttpResponse:
    return render(request, "websocket/chat.html")


def ws_alert_view(request) -> HttpResponse:
    context = {"city_uuid": request.GET.get("city_uuid")}
    return render(request, "websocket/alert.html", context)


def sse_alert_view(request) -> HttpResponse:
    context = {"city_uuid": request.GET.get("city_uuid")}
    return render(request, "eventsource/alert.html", context)


def swagger_rest_schema_view(request, resource_version: str = "v1") -> HttpResponse:
    filename = f"api.resource-{resource_version}.schema.yaml"

    file_path = os.path.join(ASSETS_API_REST_SCHEMA, filename)
    if not os.path.exists(file_path):
        return HttpResponse(status=404)

    content = ""
    with open(file_path, "rb") as file:
        content = file.read()

    return HttpResponse(content=content, headers={
        "Content-Type": "application/yaml",
        "Content-Disposition": f"attachment; filename={filename}",
    })


def swagger_ws_schema_view(request, api_version: str = "v1") -> HttpResponse:
    filename = f"{api_version}-schema.yaml"

    file_path = os.path.join(ASSETS_API_WS_SCHEMA, filename)
    if not os.path.exists(file_path):
        return HttpResponse(status=404)

    content = ""
    with open(file_path, "rb") as file:
        content = file.read()

    return HttpResponse(content=content, headers={
        "Content-Type": "application/yaml",
        "Content-Disposition": f"attachment; filename={filename}",
    })
