from tests.setup import SetupTestCase

from core.models import CityRepository


class WeatherHistoryQueryTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()

    def test_weather_history_query(self):
        city = CityRepository.get_first()
        query = f"""
        query getWeatherHistory {{
            history(
                uuid: "{city.uuid}"
                order: {{ date: DESC }}
            ) {{
                city {{
                    uuid
                    name
                }}
                date
                temperatureMaxCelsius
            }}
        }}
        """
        response = self.gql.query(query)

        self.assertIsNone(response.errors)
