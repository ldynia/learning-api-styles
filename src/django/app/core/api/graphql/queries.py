from datetime import date
from typing import Optional
from uuid import UUID

import strawberry
import strawberry_django
from strawberry_django import field
from strawberry.types import Info

from .filters import CityFilter
from .inputs import GeocodingInput
from .normalizers import notmalize_history_ordring
from .ordering import CityOrder
from .ordering import HistoryOrder
from .types import CityType
from .types import ForecastType
from .types import HistoryType
from config.constants import DOCS
from config.constants import APP_FORECAST_DAYS_MAX
from core.helpers import InputDataHandler
from core.helpers import InputDataValidator
from core.models import CityRepository
from core.models import WeatherForecastRepository
from core.models import WeatherHistoryRepository


@strawberry.type
class CityQuery:
    cities: list[CityType] = field(filters=CityFilter, order=CityOrder, description=DOCS["query"]["cities"])

@strawberry.type
class CustomCityQuery:

    @field(description=DOCS["query"]["cities"])
    def cities(self, info: Info, filters: CityFilter = None, order: CityOrder = None, includeDeleted: bool = False) -> list[CityType]:
        try:
            cities = CityRepository.get_all()
            if not includeDeleted:
                cities = cities.filter(deleted=False)
        except Exception:
            raise Exception(DOCS["errors"]["read_failed"].format("City"))

        if filters:
            cities = strawberry_django.filters.apply(filters, cities, info)

        if order:
            cities = strawberry_django.ordering.apply(order, cities)

        return cities


@strawberry.type
class WeatherQuery:

    @field(description=DOCS["query"]["geocoding"])
    def geocoding(self, info: Info, data: GeocodingInput) -> CityType:
        input, errors = InputDataHandler(InputDataValidator, request=False).valid_city_lat_lon(data)
        if errors:
            raise Exception(errors[0])

        city, lat, lon = input
        if city:
            return CityRepository.filter(name__icontains=city).first()

        return CityRepository.get_closest(lat, lon).first()

    @field(description=DOCS["query"]["forecast"])
    def forecast(self, info: Info, uuid: UUID, days: Optional[int] = APP_FORECAST_DAYS_MAX) -> list[ForecastType]:
        days, errors = InputDataHandler(InputDataValidator, request=False).handle_days(days)
        if errors:
            raise Exception(errors[0])

        city = CityRepository.get_by_id(uuid)
        if not city:
            raise Exception(DOCS["errors"]["not_found"].format("City", uuid))

        today = date.today()
        return WeatherForecastRepository.filter(city=city, date__gte=today)[:days]

    @field(description=DOCS["query"]["history"])
    def history(self, info: Info, uuid: UUID, order: Optional[HistoryOrder] = None) -> list[HistoryType]:
        sortigs = ["-date"]
        if order:
            sortigs = notmalize_history_ordring(order)

        city = CityRepository.get_by_id(uuid)
        if not city:
            raise Exception(DOCS["errors"]["not_found"].format("City", uuid))

        return WeatherHistoryRepository.filter(city=city).order_by(*sortigs)


@strawberry.type
class Query(CityQuery, WeatherQuery):
    pass

@strawberry.type
class CustomQuery(CustomCityQuery, WeatherQuery):
    pass
