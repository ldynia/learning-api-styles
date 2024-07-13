from datetime import date
from datetime import datetime
from uuid import UUID

import strawberry_django

from .ordering import CityOrder
from .ordering import ForecastOrder
from .ordering import HistoryOrder
from core.models.models import City
from core.models.models import WeatherForecast
from core.models.models import WeatherHistory


@strawberry_django.type(City, order=CityOrder)
class CityType:
    uuid: UUID
    name: str
    country: str
    region: str
    timezone: str
    latitude: float
    longitude: float
    deleted: bool


@strawberry_django.type(WeatherForecast, order=ForecastOrder)
class ForecastType:
    city: CityType
    date: date
    rain_sum_mm: float
    showers_sum_mm: float
    snowfall_sum_cm: float
    sunrise_iso8601: datetime
    sunset_iso8601: datetime
    temperature_max_celsius: float
    temperature_min_celsius: float
    uv_index_max: float
    wind_speed_max_kmh: float


@strawberry_django.type(WeatherHistory, order=HistoryOrder)
class HistoryType:
    city: CityType
    date: date
    rain_sum_mm: float
    snowfall_sum_cm: float
    sunrise_iso8601: datetime
    sunset_iso8601: datetime
    temperature_max_celsius: float
    temperature_min_celsius: float
    wind_speed_max_kmh: float
