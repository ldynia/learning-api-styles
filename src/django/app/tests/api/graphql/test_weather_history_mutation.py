from tests.setup import SetupTestCase

from config.constants import APP_DEFAULT_YEAR
from core.models import CityRepository


class WeatherHistoryMutationTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.headers = {
            "Authorization": f"Bearer {self.get_jwt_token_gql()}"
        }

    def test_seed_city_weather_history(self):
        city = CityRepository.get_first()
        query = f"""
        mutation {{
            seedCityWeatherHistory(uuid: "{city.uuid}", data: {{year: {APP_DEFAULT_YEAR}}})
        }}
        """

        response = self.gql.query(query, headers=self.headers)

        self.assertIsNone(response.errors)

    def test_seed_city_weather_history_no_input(self):
        city = CityRepository.get_first()
        query = f"""
        mutation {{
            seedCityWeatherHistory(uuid: "{city.uuid}", data: {{}})
        }}
        """
        response = self.gql.query(query, headers=self.headers)

        self.assertIsNone(response.errors)

    def test_seed_all_cities_weather_history(self):
        query = f"""
        mutation {{
            seedAllCitiesWeatherHistory(data: {{year: {APP_DEFAULT_YEAR}}})
        }}
        """

        response = self.gql.query(query, headers=self.headers)

        self.assertIsNone(response.errors)

    def test_seed_all_cities_weather_history_no_input(self):
        query = f"""
        mutation {{
            seedAllCitiesWeatherHistory(data: {{}})
        }}
        """
        response = self.gql.query(query, headers=self.headers)

        self.assertIsNone(response.errors)
