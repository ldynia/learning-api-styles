from datetime import date
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry
import strawberry_django

from .ordering import CityOrder
from .ordering import ForecastOrder
from .ordering import HistoryOrder
from core.models.models import City
from core.models.models import WeatherForecast
from core.models.models import WeatherHistory


def to_float(value):
    return float(value) if isinstance(value, Decimal) else value


@strawberry_django.type(City, order=CityOrder)
class CityType:
    uuid: UUID
    name: str
    country: str
    region: str
    timezone: str
    latitude: float = strawberry_django.field(resolver=lambda root: to_float(root.latitude), only=["latitude"])
    longitude: float = strawberry_django.field(resolver=lambda root: to_float(root.longitude), only=["longitude"])
    deleted: bool


@strawberry_django.type(WeatherForecast, order=ForecastOrder)
class ForecastType:
    city: CityType
    date: date
    rain_sum_mm: float = strawberry_django.field(resolver=lambda root: to_float(root.rain_sum_mm), only=["rain_sum_mm"])
    showers_sum_mm: float = strawberry_django.field(resolver=lambda root: to_float(root.showers_sum_mm), only=["showers_sum_mm"])
    snowfall_sum_cm: float = strawberry_django.field(resolver=lambda root: to_float(root.snowfall_sum_cm), only=["snowfall_sum_cm"])
    sunrise_iso8601: datetime
    sunset_iso8601: datetime
    temperature_max_celsius: float = strawberry_django.field(resolver=lambda root: to_float(root.temperature_max_celsius), only=["temperature_max_celsius"])
    temperature_min_celsius: float = strawberry_django.field(resolver=lambda root: to_float(root.temperature_min_celsius), only=["temperature_min_celsius"])
    uv_index_max: float = strawberry_django.field(resolver=lambda root: to_float(root.uv_index_max), only=["uv_index_max"])
    wind_speed_max_kmh: float = strawberry_django.field(resolver=lambda root: to_float(root.wind_speed_max_kmh), only=["wind_speed_max_kmh"])


@strawberry_django.type(WeatherHistory, order=HistoryOrder)
class HistoryType:
    city: CityType
    date: date
    rain_sum_mm: float = strawberry_django.field(resolver=lambda root: to_float(root.rain_sum_mm), only=["rain_sum_mm"])
    snowfall_sum_cm: float = strawberry_django.field(resolver=lambda root: to_float(root.snowfall_sum_cm), only=["snowfall_sum_cm"])
    sunrise_iso8601: datetime
    sunset_iso8601: datetime
    temperature_max_celsius: float = strawberry_django.field(resolver=lambda root: to_float(root.temperature_max_celsius), only=["temperature_max_celsius"])
    temperature_min_celsius: float = strawberry_django.field(resolver=lambda root: to_float(root.temperature_min_celsius), only=["temperature_min_celsius"])
    wind_speed_max_kmh: float = strawberry_django.field(resolver=lambda root: to_float(root.wind_speed_max_kmh), only=["wind_speed_max_kmh"])
