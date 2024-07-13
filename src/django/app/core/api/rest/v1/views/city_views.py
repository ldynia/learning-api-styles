from rest_framework.decorators import throttle_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_412_PRECONDITION_FAILED
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.throttling import AnonRateThrottle

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from config import to_boolean
from config.constants import CACHE_TIMEOUT_SECONDS
from config.constants import DOCS
from config.constants import REST_FRAMEWORK
from core.helpers import error_response
from core.helpers import get_errors
from core.helpers import InputDataHandler
from core.helpers import InputDataValidator
from core.helpers import IsSuperuser
from core.helpers import success_response
from core.helpers import success_response_paginated
from core.helpers.serializers import CitySerializer
from core.helpers.utils import get_serializer_errors
from core.models import CityRepository


class CityView(GenericAPIView):
    allowed_methods = ["GET", "PATCH", "PUT", "DELETE"]
    input_handler = InputDataHandler(InputDataValidator)
    permission_classes = [IsAuthenticated & IsSuperuser]
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.request.version == REST_FRAMEWORK["DEFAULT_VERSION"]:
            return CitySerializer

        return super().get_serializer_class()

    def get_permissions(self):
        # Exempt GET requests from authentication
        if self.request.method == "GET":
            return []

        return super().get_permissions()

    @method_decorator(cache_page(CACHE_TIMEOUT_SECONDS))
    def get(self, request, uuid):
        allowed_fields = self.serializer_class.Meta.fields
        fields, errors = self.input_handler.handle_fields(request, allowed_fields)

        errors = get_errors(errors)
        if errors:
            return error_response(errors)

        try:
            city = CityRepository.get_by_id(uuid)
        except Exception:
            errors = [DOCS["errors"]["read_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not city:
            errors = DOCS["errors"]["not_found"].format("City", uuid)
            return error_response(errors, HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(city, fields=fields)

        return success_response(serializer.data)

    def patch(self, request, uuid):
        try:
            city = CityRepository.get_by_id(uuid)
        except Exception:
            errors = [DOCS["errors"]["read_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not city or city.deleted:
            errors = DOCS["errors"]["not_found"].format("City", uuid)
            return error_response(errors, HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(city, data=request.data, partial=True)

        if not serializer.is_valid():
            errors = get_serializer_errors(serializer)
            return error_response(errors)

        try:
            serializer.save()
        except Exception:
            errors = DOCS["errors"]["update_failed"].format("City", uuid)
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        return success_response(serializer.data)

    def put(self, request, uuid):
        try:
            city = CityRepository.get_by_id(uuid)
        except Exception:
            errors = [DOCS["errors"]["read_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not city or city.deleted:
            errors = DOCS["errors"]["not_found"].format("City", uuid)
            return error_response(errors, HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(city, data=request.data)

        if not serializer.is_valid():
            errors = get_serializer_errors(serializer)
            return error_response(errors)

        try:
            serializer.save()
        except Exception:
            errors = DOCS["errors"]["update_failed"].format("City", uuid)
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        return success_response(serializer.data)

    def delete(self, request, uuid):
        soft_delete = to_boolean(request.query_params.get("soft_delete", True))

        try:
            city = CityRepository.get_by_id(uuid)
        except Exception:
            errors = [DOCS["errors"]["read_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not city:
            errors = DOCS["errors"]["not_found"].format("City", uuid)
            return error_response(errors, HTTP_404_NOT_FOUND)

        double_soft_delete = (city and city.deleted and soft_delete)
        if double_soft_delete:
            errors = DOCS["errors"]["soft_delete"].format("City", uuid)
            return error_response(errors, HTTP_412_PRECONDITION_FAILED)

        city = CityRepository.delete(uuid, soft_delete)
        if not city:
            errors = [DOCS["errors"]["delete_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(city)

        return success_response(serializer.data)


class CityListView(GenericAPIView):
    allowed_methods = ["GET", "POST"]
    input_handler = InputDataHandler(InputDataValidator)
    permission_classes = [IsAuthenticated & IsSuperuser]
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.request.version == REST_FRAMEWORK["DEFAULT_VERSION"]:
            return CitySerializer

        return super().get_serializer_class()

    def get_permissions(self):
        # Exempt GET requests from authentication
        if self.request.method == "GET":
            return []

        return super().get_permissions()

    @throttle_classes([AnonRateThrottle])
    @method_decorator(cache_page(CACHE_TIMEOUT_SECONDS))
    def get(self, request):
        allowed_fields = self.serializer_class.Meta.fields
        fields, fields_errors = self.input_handler.handle_fields(request, allowed_fields)
        search, search_errors = self.input_handler.handle_search(request, allowed_fields)
        sort, sort_errors = self.input_handler.handle_sort(request, allowed_fields)
        include_deleted = to_boolean(request.query_params.get("include_deleted", False))

        errors = get_errors(fields_errors + sort_errors + search_errors)
        if errors:
            return error_response(errors)

        try:
            cities = CityRepository.get_all().order_by(sort).filter(**search)
            if not include_deleted:
                cities = cities.filter(deleted=False)
        except Exception:
            errors = [DOCS["errors"]["read_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        return success_response_paginated(self.serializer_class, request, cities, fields)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            errors = get_serializer_errors(serializer)
            return error_response(errors)

        try:
            serializer.save()
        except Exception:
            errors = DOCS["errors"]["creation_failed"].format("City")
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        return success_response(serializer.data, HTTP_201_CREATED)
