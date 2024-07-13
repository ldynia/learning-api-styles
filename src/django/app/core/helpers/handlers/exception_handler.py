from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

from config.base import logger


def request_exception_handler(exception: APIException, context: dict) -> Response:
    response = exception_handler(exception, context)
    if response and response.status_code >= 400:
        logger.error({
            "status_code": response.status_code,
            "http_method": context["request"].method,
            "path": context["request"].path,
            "error": str(response.data['detail']),
        })

        # prevent repsonse from being logged again by "django.request" logger
        setattr(response, "_has_been_logged", True)

    return response
