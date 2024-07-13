import requests
from datetime import datetime

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_424_FAILED_DEPENDENCY
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from config.constants import APP_FORECAST_DAYS_MAX
from config.constants import DOCS
from config.constants import OM_API_CALL_TIMEOUT_SECONDS
from config.constants import OM_API_FORECAST_ENDPOINT
from config.constants import REST_FRAMEWORK

from core.helpers import error_response
from core.helpers import get_errors
from core.helpers import InputDataHandler
from core.helpers import InputDataValidator
from core.helpers import IsSuperuser
from core.helpers import success_response
from core.helpers.serializers import WeatherForecastSerializer
from core.helpers.serializers import WeatherHistorySerializer
from core.models import CityRepository
from core.models import WeatherForecast
from core.models import WeatherForecastRepository
from core.models import WeatherHistoryRepository
from core.models import WeatherHistorySeed


class WeatherForecastListView(GenericAPIView):
    allowed_methods = ["GET"]
    serializer_class = WeatherForecastSerializer

    def get_serializer_class(self):
        if self.request.version == REST_FRAMEWORK["DEFAULT_VERSION"]:
            return WeatherForecastSerializer

        return super().get_serializer_class()

    def get(self, request):
        allowed_fields = self.serializer_class.Meta.fields
        fields, err_fileds = InputDataHandler(InputDataValidator).handle_fields(request, allowed_fields)
        first_n_days, err_days = InputDataHandler(InputDataValidator).handle_days(request)
        uuid, err_uuid = InputDataHandler(InputDataValidator).handle_city_uuid(request)

        errors = get_errors(err_days + err_fileds + err_uuid)
        if errors:
            return error_response(errors)

        try:
            city = CityRepository.filter(uuid=uuid).first()
        except Exception:
            errors = [DOCS["errors"]["read_failed"].format("City")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)
        if not city:
            err = DOCS["errors"]["not_found"].format("City", uuid)
            return error_response(err, HTTP_404_NOT_FOUND)

        query_params = {
            "daily": [
                "rain_sum",
                "showers_sum",
                "snowfall_sum",
                "sunrise",
                "sunset",
                "temperature_2m_max",
                "temperature_2m_min",
                "uv_index_max",
                "windspeed_10m_max",
            ],
            "forecast_days": APP_FORECAST_DAYS_MAX,
            "latitude": city.latitude,
            "longitude": city.longitude,
            "timezone": city.timezone,
        }

        # Get data from external API
        try:
            response = requests.get(OM_API_FORECAST_ENDPOINT, query_params, timeout=OM_API_CALL_TIMEOUT_SECONDS)
            if response.status_code != 200:
                err = ["Failed to obtain data from an external service."]
                return error_response(err, HTTP_424_FAILED_DEPENDENCY)
        except requests.exceptions.Timeout:
            err = ["Failed to obtain data from an external service."]
            return error_response(err, HTTP_424_FAILED_DEPENDENCY)
        except Exception:
            err = ["Failed to obtain data from an external service."]
            return error_response(err, HTTP_424_FAILED_DEPENDENCY)

        try:
            today = datetime.today().strftime("%Y-%m-%d")
            today_weather = WeatherForecastRepository.filter(city=city, date=today).first()
        except Exception:
            errors = [DOCS["errors"]["filter_failed"].format("WeatherForecast")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not today_weather:
            try:
                # Delete all not today's records
                WeatherForecastRepository.filter(city=city).delete()
            except Exception:
                errors = [DOCS["errors"]["delete_failed"].format("WeatherForecast")]
                return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        forecast = []
        response_data = response.json()
        weather_forecast = WeatherForecastRepository.filter(city=city, date__in=response_data["daily"]["time"])
        if not weather_forecast:
            for idx, date in enumerate(response_data["daily"]["time"]):
                forecast.append(
                    WeatherForecast(
                        city=city,
                        date=date,
                        rain_sum_mm=response_data["daily"]["rain_sum"][idx],
                        showers_sum_mm=response_data["daily"]["showers_sum"][idx],
                        snowfall_sum_cm=response_data["daily"]["snowfall_sum"][idx],
                        sunrise_iso8601=response_data["daily"]["sunrise"][idx],
                        sunset_iso8601=response_data["daily"]["sunset"][idx],
                        temperature_max_celsius=response_data["daily"]["temperature_2m_max"][idx],
                        temperature_min_celsius=response_data["daily"]["temperature_2m_min"][idx],
                        uv_index_max=response_data["daily"]["uv_index_max"][idx],
                        wind_speed_max_kmh=response_data["daily"]["windspeed_10m_max"][idx],
                    )
                )
            WeatherForecastRepository.create(forecast)
            weather_forecast = WeatherForecastRepository.filter().select_related().all()

        serializer = self.get_serializer(weather_forecast[:first_n_days], many=True, fields=fields)

        return success_response(serializer.data)


class WeatherHistoryListView(GenericAPIView):
    allowed_methods = ["GET"]
    serializer_class = WeatherHistorySerializer

    def get(self, request):
        allowed_fields = self.serializer_class.Meta.fields
        fields, err_fileds = InputDataHandler(InputDataValidator).handle_fields(request, allowed_fields)
        dates, err_dates = InputDataHandler(InputDataValidator).handle_dates(request)
        uuid, err_uuid = InputDataHandler(InputDataValidator).handle_city_uuid(request)

        errors = get_errors(err_dates + err_fileds + err_uuid)
        if errors:
            return error_response(errors)

        try:
            city = CityRepository.filter(uuid=uuid).first()
        except Exception:
            errors = [DOCS["errors"]["not_found"].format("City", uuid)]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not city:
            err = DOCS["errors"]["not_found"].format("City", uuid)
            return error_response(err, HTTP_404_NOT_FOUND)

        try:
            if not dates:
                weather_history = WeatherHistoryRepository.filter(city=city).select_related().order_by("date")
            else:
                weather_history = WeatherHistoryRepository.filter(city=city, date__range=dates).select_related().order_by("date")
        except Exception:
            errors = [DOCS["errors"]["filter_failed"].format("WeatherHistory")]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(weather_history, many=True, fields=fields)

        return success_response(serializer.data)


class WeatherSeedView(GenericAPIView):
    """Seed weather history for a specific city or all cities."""

    allowed_methods = ["PUT"]
    permission_classes = [IsAuthenticated & IsSuperuser]
    serializer_class = WeatherHistorySerializer

    def put(self, request):
        uuid, err_uuid = InputDataHandler(InputDataValidator, query=False).handle_city_uuid(request)
        year, err_year = InputDataHandler(InputDataValidator, query=False).handle_year(request)

        errors = get_errors(err_uuid + err_year)
        if errors:
            return error_response(errors)

        try:
            cities = self.__get_cities(uuid)
        except Exception:
            errors = ["Failed to filter cities."]
            return error_response(errors, HTTP_500_INTERNAL_SERVER_ERROR)

        if not cities:
            return error_response(["Could not find requested city or cities."], HTTP_404_NOT_FOUND)

        # Seed weather history
        seeded, err = WeatherHistorySeed(year).seed(cities, False)
        if not seeded:
            return error_response([err], HTTP_424_FAILED_DEPENDENCY)

        return success_response(None, HTTP_204_NO_CONTENT)

    def __get_cities(self, uuid):
        if uuid:
            return CityRepository.filter(uuid=uuid)

        return CityRepository.get_all()
