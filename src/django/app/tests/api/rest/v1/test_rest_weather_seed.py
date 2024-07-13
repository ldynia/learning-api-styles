from datetime import datetime

from rest_framework.status import HTTP_204_NO_CONTENT

from core.api.rest.v1 import WeatherSeedView
from core.models import CityRepository
from core.models import WeatherHistoryRepository
from tests.setup import SetupTestCase


class WeatherSeedTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.get_jwt_token_rest()}",
        }
        self.repository = CityRepository
        self.view = WeatherSeedView.as_view()
        self.year = 1984

    def test_weather_seed_one_city(self):
        city = self.repository.get_first()
        wh_before_count = WeatherHistoryRepository.get_count()

        data = {"year": self.year, "city_uuid": city.uuid}
        request = self.factory.put("api/seed", data, format="json", **self.headers)
        response = self.view(request)

        wh_after_count = WeatherHistoryRepository.get_count()

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertGreater(wh_after_count, wh_before_count)

    def test_weather_seed_all_city(self):
        wh_before_count = WeatherHistoryRepository.get_count()

        data = {"year": self.year}
        request = self.factory.put("api/seed", data, format="json", **self.headers)
        response = self.view(request)

        wh_after_count = WeatherHistoryRepository.get_count()

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertGreater(wh_after_count, wh_before_count)

    def test_weather_seed_current_year(self):
        wh_before_count = WeatherHistoryRepository.get_count()

        data = {"year": datetime.now().year}
        request = self.factory.put("api/seed", data, format="json", **self.headers)
        response = self.view(request)

        wh_after_count = WeatherHistoryRepository.get_count()

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        self.assertGreaterEqual(wh_after_count, wh_before_count)
