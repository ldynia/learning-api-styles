from typing import Optional
from uuid import UUID

from strawberry import field
import strawberry
import strawberry_django

from config.constants import APP_DEFAULT_YEAR
from config.constants import DOCS
from core.models import City


@strawberry.input(description=DOCS["input"]["seed"])
class SeedInput:
    year: int = APP_DEFAULT_YEAR


@strawberry.input(description=DOCS["input"]["geocoding"])
class GeocodingInput:
    city: Optional[str] = field(
        default=None,
        description=DOCS["input_field"]["city"]
    )
    latitude: Optional[float] = field(
        default=None, description=DOCS["input_field"]["latitude"]
    )
    longitude: Optional[float] = field(
        default=None, description=DOCS["input_field"]["longitude"]
    )


@strawberry_django.input(City)
class UUIDInput:
    uuid: UUID
    soft_delete: Optional[bool] = True


@strawberry_django.input(City)
class CityInput:
    name: str
    country: str
    region: str
    timezone: str
    latitude: float
    longitude: float


@strawberry_django.partial(City)
class CityInputPartial(UUIDInput):
    name: Optional[str]
    country: Optional[str]
    region: Optional[str]
    timezone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
