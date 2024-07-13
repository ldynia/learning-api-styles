from datetime import datetime

from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_424_FAILED_DEPENDENCY

from config.base import REST_FRAMEWORK
from config.constants import APP_DEFAULT_YEAR
from config.constants import OM_API_DATE_END
from core.api.rest.v1 import WeatherForecastListView
from core.api.rest.v1 import WeatherHistoryListView
from core.models import CityRepository
from core.models import WeatherForecastRepository
from core.models import WeatherHistoryRepository
from tests.setup import SetupTestCase


class WeatherForecstTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.view = WeatherForecastListView.as_view()
        self.cityRepo = CityRepository
        self.forecastRepo = WeatherForecastRepository

    def test_weather_forecast_success(self):
        """
        If API call returns HTTP_424_FAILED_DEPENDENCY I consider it as success too!
        """
        city = self.cityRepo.filter(name="Tokyo").first()
        before_count = self.forecastRepo.get_all().count()

        query_params = {"city_uuid": city.uuid, "days": 1}
        request = self.factory.get(f"api/forecasts", query_params)
        response = self.view(request)

        after_count = self.forecastRepo.get_all().count()

        self.assertIn(response.status_code, [HTTP_200_OK, HTTP_424_FAILED_DEPENDENCY])
        self.assertGreaterEqual(after_count, before_count)

    def test_weather_forecast_for_new_city(self):
        city = self.cityRepo.create(
            name="Kyoto",
            country="Japan",
            region="Asia",
            latitude=35.02107,
            longitude=135.75385,
            timezone="Asia/Tokyo"
        )
        query_params = {"city_uuid": city.uuid}
        request = self.factory.get(f"api/forecasts", query_params)
        response = self.view(request)

        self.assertIn(response.status_code, [HTTP_200_OK, HTTP_424_FAILED_DEPENDENCY])

    def test_weather_forecast_query_param_days(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {"city_uuid": city.uuid, "days": 8}
        request = self.factory.get(f"api/forecasts", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_weather_query_param_valid_version(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {"city_uuid": city.uuid, "version": REST_FRAMEWORK["DEFAULT_VERSION"]}
        request = self.factory.get(f"api/forecasts", query_params)
        response = self.view(request)

        self.assertIn(response.status_code, [HTTP_200_OK, HTTP_424_FAILED_DEPENDENCY])

    def test_weather_query_param_invalid_version(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {"city_uuid": city.uuid, "version": "x.y.z"}
        request = self.factory.get(f"api/forecasts", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class WeatherHistoryTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.view = WeatherHistoryListView.as_view()
        self.cityRepo = CityRepository
        self.forecastRepo = WeatherHistoryRepository

    def test_weather_history_success(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {"city_uuid": city.uuid}
        request = self.factory.get(f"api/history", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_weather_history_success_with_date(self):
        city = self.cityRepo.filter(name="Tokyo").first()
        start_date = f"{APP_DEFAULT_YEAR}-01-01"

        # Shift end date by 2 days back
        end_date = OM_API_DATE_END
        if datetime.now().day > 3:
            end_date = f"{APP_DEFAULT_YEAR}-{datetime.now().month:02d}-{datetime.now().day-2:02d}"

        query_params = {
            "city_uuid": city.uuid,
            "fields": "sunrise_iso8601,sunset_iso8601",
            "start_date": start_date,
            "end_date": end_date
        }
        request = self.factory.get(f"api/history", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_weather_history_query_params_dates(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {
            "city_uuid": city.uuid,
            "start_date": "1234-56",
            "end_date": "xxx"
        }
        request = self.factory.get(f"api/history", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_weather_history_query_params_dates_range(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {
            "city_uuid": city.uuid,
            "start_date": "1939-01-01",
            "end_date": "2025-01-01"
        }
        request = self.factory.get(f"api/history", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_weather_history_query_params_dates_mssing(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {"city_uuid": city.uuid, "end_date": f"{APP_DEFAULT_YEAR}-01-01"}
        request = self.factory.get(f"api/history", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_history_query_param_valid_version(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {"city_uuid": city.uuid, "version": REST_FRAMEWORK["DEFAULT_VERSION"]}
        request = self.factory.get(f"api/history", query_params)
        response = self.view(request)

        self.assertIn(response.status_code, [HTTP_200_OK])

    def test_history_query_param_invalid_version(self):
        city = self.cityRepo.filter(name="Tokyo").first()

        query_params = {"city_uuid": city.uuid, "version": "x.y.z"}
        request = self.factory.get(f"api/history", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
