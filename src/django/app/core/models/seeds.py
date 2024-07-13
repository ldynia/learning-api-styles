from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import Tuple
import json
import requests

from django.contrib.auth.hashers import make_password

from config.constants import ASSETS_DB_CITIES
from config.constants import ASSETS_DB_FORECAST
from config.constants import ASSETS_DB_HISTORY
from config.constants import OM_API_ARCHIVE_ENDPOINT
from config.constants import OM_API_CALL_TIMEOUT_SECONDS
from config.constants import OM_API_YEAR_END
from core.helpers.utils import to_default
from core.models import City
from core.models import CityRepository
from core.models import UserRepository
from core.models import WeatherForecast
from core.models import WeatherForecastRepository
from core.models import WeatherHistory
from core.models import WeatherHistoryRepository


class AdminSeed:

    def seed(self) -> Tuple[bool, str]:
        user = UserRepository.filter(username="admin").first()
        if not user:
            UserRepository.create(
                username="admin",
                email="admin@localhost",
                password=make_password("admin"),
                is_superuser=True
            )
        return True, ""


class CitySeed:

    def seed(self) -> Tuple[bool, str]:
        try:
            with open(ASSETS_DB_CITIES) as file:
                cities = []
                for city in json.load(file):
                    if not CityRepository.filter(name=city["name"]):
                        cities.append(City(
                            name=city["name"],
                            country=city["country"],
                            region=city["region"],
                            latitude=city["latitude"],
                            longitude=city["longitude"],
                            timezone=city["timezone"]
                        ))
                CityRepository.create(cities)
            return True, ""
        except Exception:
            return False, f"Failed save data to {City._meta.db_table} table."


class WeatherForecastSeed:

    def seed(self) -> Tuple[bool, str]:
        with open(ASSETS_DB_FORECAST) as file:
            data = []
            forecasts = self.__normalize_forecast(json.load(file))
            for city_id, city_forecasts in forecasts.items():
                for forecast in city_forecasts:
                    weather_forecast = WeatherForecastRepository.filter(city_id=city_id, date=forecast["date"]).first()
                    if not weather_forecast:
                        data.append(WeatherForecast(
                            city_id=city_id,
                            date=forecast["date"],
                            rain_sum_mm=to_default(forecast["rain_sum_mm"], 0),
                            showers_sum_mm=to_default(forecast["showers_sum_mm"], 0),
                            snowfall_sum_cm=to_default(forecast["snowfall_sum_cm"], 0),
                            sunrise_iso8601=forecast["sunrise_iso8601"],
                            sunset_iso8601=forecast["sunset_iso8601"],
                            temperature_max_celsius=to_default(forecast["temperature_max_celsius"], 0),
                            temperature_min_celsius=to_default(forecast["temperature_min_celsius"], 0),
                            uv_index_max=to_default(forecast["uv_index_max"], 0),
                            wind_speed_max_kmh=to_default(forecast["wind_speed_max_kmh"], 0)
                        ))
            WeatherForecastRepository.create(data)

        return True, ""

    def __normalize_forecast(self, forecasts) -> Dict[int, list]:
        data = {}
        for forecast in forecasts:
            if forecast["city_id"] not in data:
                forecast["date"] = datetime.today().strftime("%Y-%m-%d")
                data[forecast["city_id"]] = [forecast]
            else:
                next_day_increment = len(data[forecast["city_id"]])
                following_day = datetime.today() + timedelta(days=next_day_increment)
                forecast["date"] = following_day.strftime("%Y-%m-%d")
                data[forecast["city_id"]].append(forecast)

        return data


class WeatherHistorySeed:

    def __init__(self, year):
        self.year = year

    def __get_end_date(self) -> Tuple[bool, str]:
        if self.year == OM_API_YEAR_END:
            yesterday = (datetime.now() - timedelta(days=1))
            return yesterday.strftime("%Y-%m-%d")

        return f"{self.year}-12-31"

    def seed(self, cities: [City], from_assets: bool) -> Tuple[bool, str]:
        if from_assets:
            with open(ASSETS_DB_HISTORY, encoding="utf-8") as file:
                histories = []
                for history in json.load(file):
                    weather_history = WeatherHistoryRepository.filter(city_id=history["city_id"], date=history["date"]).first()
                    if not weather_history:
                        histories.append(WeatherHistory(
                            city_id=history["city_id"],
                            date=history["date"],
                            rain_sum_mm=to_default(history["rain_sum_mm"], 0),
                            snowfall_sum_cm=to_default(history["snowfall_sum_cm"], 0),
                            sunrise_iso8601=history["sunrise_iso8601"],
                            sunset_iso8601=history["sunset_iso8601"],
                            temperature_max_celsius=to_default(history["temperature_max_celsius"], 0),
                            temperature_min_celsius=to_default(history["temperature_min_celsius"], 0),
                            wind_speed_max_kmh=to_default(history["wind_speed_max_kmh"], 0)
                        ))
                WeatherHistoryRepository.create(histories)
            return True, ""

        for city in cities:
            query_params = {
                "daily": [
                    "rain_sum",
                    "snowfall_sum",
                    "sunrise",
                    "sunset",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "windspeed_10m_max"
                ],
                "start_date": f"{self.year}-01-01",
                "end_date": self.__get_end_date(),
                "latitude": city.latitude,
                "longitude": city.longitude,
                "timezone": city.timezone,
            }
            try:
                response = requests.get(OM_API_ARCHIVE_ENDPOINT, query_params, timeout=OM_API_CALL_TIMEOUT_SECONDS, verify=True)
                if response.status_code != 200:
                    return False, f"Failed obtaining data for {city.name} got {response.status_code} from {OM_API_ARCHIVE_ENDPOINT}, reason: {response.text}"
            except Exception as e:
                    return False, f"Failed obtaining data for {city.name} from {OM_API_ARCHIVE_ENDPOINT}, reason: {e}"

            history = []
            response_data = response.json()
            data = WeatherHistoryRepository.filter(city=city, date__in=response_data["daily"]["time"])
            if not data:
                for idx, date in enumerate(response_data["daily"]["time"]):
                    history.append(WeatherHistory(
                        city=city,
                        date=date,
                        rain_sum_mm=to_default(response_data["daily"]["rain_sum"][idx], 0),
                        snowfall_sum_cm=to_default(response_data["daily"]["snowfall_sum"][idx], 0),
                        sunrise_iso8601=response_data["daily"]["sunrise"][idx],
                        sunset_iso8601=response_data["daily"]["sunset"][idx],
                        temperature_max_celsius=to_default(response_data["daily"]["temperature_2m_max"][idx], 0),
                        temperature_min_celsius=to_default(response_data["daily"]["temperature_2m_min"][idx], 0),
                        wind_speed_max_kmh=to_default(response_data["daily"]["windspeed_10m_max"][idx], 0),
                    ))
                WeatherHistoryRepository.create(history)

        return True, ""
