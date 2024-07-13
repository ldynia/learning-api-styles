import strawberry_django
from strawberry import auto

from config.constants import DOCS
from core.models import City
from core.models import WeatherForecast
from core.models import WeatherHistory


@strawberry_django.order(City, description=DOCS["order"]["city"])
class CityOrder:
    name: auto
    country: auto
    region: auto
    timezone: auto


@strawberry_django.order(WeatherForecast, description=DOCS["order"]["forecast"])
class ForecastOrder:
    date: auto


@strawberry_django.order(WeatherHistory, description=DOCS["order"]["history"])
class HistoryOrder:
    date: auto
    rain_sum_mm: auto
    snowfall_sum_cm: auto
    sunrise_iso8601: auto
    sunset_iso8601: auto
    temperature_max_celsius: auto
    temperature_min_celsius: auto
    wind_speed_max_kmh: auto
