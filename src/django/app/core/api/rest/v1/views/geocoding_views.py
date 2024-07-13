from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from config.constants import DOCS
from config.constants import REST_FRAMEWORK
from core.helpers import error_response
from core.helpers import get_errors
from core.helpers import InputDataHandler
from core.helpers import InputDataValidator
from core.helpers import success_response
from core.helpers.serializers import CitySerializer
from core.models import CityRepository


class GeocodingView(GenericAPIView):
    allowed_methods = ["GET"]
    serializer_class = CitySerializer

    def get_serializer_class(self):
        if self.request.version == REST_FRAMEWORK["DEFAULT_VERSION"]:
            return CitySerializer

        return super().get_serializer_class()

    def get(self, request):
        allowed_fields = self.serializer_class.Meta.fields
        fields, fields_errors = InputDataHandler(InputDataValidator).handle_fields(request, allowed_fields)
        query_params, cll_errors = InputDataHandler(InputDataValidator).valid_city_lat_lon(request)

        errors = get_errors(cll_errors + fields_errors)
        if errors:
            return error_response(errors)

        try:
            city_name, lat, lon = query_params
            city = self.__get_city(city_name, lat, lon)
        except Exception:
            errors = [DOCS["errors"]["filter_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not city:
            errors = [DOCS["errors"]["not_found"].format("City", city_name)]
            return error_response(errors, HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(city, fields=fields)

        return success_response(serializer.data)

    def __get_city(self, name, lat, lon):
        if name:
            return CityRepository.filter(name__icontains=name).first()

        return CityRepository.get_closest(lat, lon).first()
