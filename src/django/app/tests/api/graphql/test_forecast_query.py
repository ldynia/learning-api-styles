from tests.setup import SetupTestCase

from core.models import CityRepository
from config.constants import APP_FORECAST_DAYS_MAX


class ForecastQueryTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()

    def test_forecast_query(self):
        city = CityRepository.get_first()
        query = f"""
        query getWeatherForecast {{
            forecast(uuid: "{city.uuid}") {{
                city {{
                   name
                    uuid
                }}
                date
                rainSumMm
                showersSumMm
                snowfallSumCm
                sunriseIso8601
                sunsetIso8601
                temperatureMaxCelsius
                temperatureMinCelsius
                uvIndexMax
                windSpeedMaxKmh
            }}
        }}
        """
        response = self.gql.query(query)

        self.assertIsNone(response.errors)

    def test_forecast_invalid_input_query(self):
        city = CityRepository.get_first()
        query = f"""
        query getWeatherForecast {{
            forecast(uuid: "{city.uuid}", days: {APP_FORECAST_DAYS_MAX}) {{
                city {{
                   name
                    uuid
                }}
                date
                rainSumMm
                showersSumMm
                snowfallSumCm
                sunriseIso8601
                sunsetIso8601
                temperatureMaxCelsius
                temperatureMinCelsius
                uvIndexMax
                windSpeedMaxKmh
            }}
        }}
        """
        response = self.gql.query(query)

        self.assertIsNone(response.errors)
