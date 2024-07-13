from typing import Any
from typing import Dict
from typing import List
from typing import Set

from django.db.models.query import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_400_BAD_REQUEST

from config.constants import REST_FRAMEWORK
from core.helpers.handlers.pagination_handler import PageNumberPaginationHATEOAS


def get_errors(error: List[str | List[str]] = []) -> Set[str]:
    """
    Gather error messages into a set.

    Args:
        error (list): A list of error messages. Each error message can be a string or a list of strings.
        status (int): The HTTP status code to set in the response.

    Returns:
        Response or None: The error response with error messages or None if no error are provided.
    """
    err_msgs = set()
    if len(error) and isinstance(error, str):
        err_msgs.add(error)

    if len(error) and isinstance(error, list):
        for err in error:
            err_msgs.add(err)

    return err_msgs


def error_response(errors: List[str | List[str]], status_code: int = HTTP_400_BAD_REQUEST) -> Response:
    """
    Create and log an error response with error messages.

    Args:
        errors (list): A list of error messages. Each error message can be a string or a list of strings.
        status_code (int): The HTTP status code to set in the response.

    Returns:
        Response: The error response with error messages.
    """
    return Response({"errors": errors}, status=status_code)


def success_response(data: Dict[str, Any] | None = None, status_code: int = HTTP_200_OK) -> Response:
    """
    Create a success response with optional data.

    Args:
        data (dict): A dictionary containing data to include in the response.
        status_code (int): The HTTP status code to set in the response.

    Returns:
        Response: The success response with data, if provided.
    """
    if not data:
        return Response(None, status=status_code)

    return Response({"results": [data]}, status=status_code)


def success_response_paginated(serializer: Any, request: Request, queryset: QuerySet, fields: set = None) -> Response:
    """Generate a paginated success response.

    Args:
        serializer (Any): The serializer class to serialize the data.
        request (Request): The HTTP request object.
        queryset (QuerySet): The queryset to paginate.
        fields (set): Fields to include in the response.

    Returns:
        Response: An HTTP response with paginated serialized data.
    """
    page_size = int(request.query_params.get("page_size", REST_FRAMEWORK["PAGE_SIZE"]))

    # paginator = PageNumberPaginationHATEOAS()
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    paginated_serializer = serializer(paginated_queryset, many=True, fields=fields)

    return paginator.get_paginated_response(paginated_serializer.data)
