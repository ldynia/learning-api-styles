from typing import Optional

import strawberry_django

from core.helpers.filters import NumericFilterLookup
from core.helpers.filters import TextFilterLookup
from core.models import City


@strawberry_django.filter(City, lookups=True)
class CityFilter:
    name: Optional[TextFilterLookup[str]]
    country: Optional[TextFilterLookup[str]]
    region: Optional[TextFilterLookup[str]]
    timezone: Optional[TextFilterLookup[str]]
    latitude: Optional[NumericFilterLookup[float]]
    longitude: Optional[NumericFilterLookup[float]]
