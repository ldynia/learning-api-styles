from uuid import UUID
from typing import Any
from typing import Dict
from typing import Tuple

from django.contrib.auth.models import User
from django.db.models.expressions import RawSQL
from django.db.models.query import QuerySet
from django.utils import timezone
from gqlauth.models import UserStatus

from core.models import City
from core.models import WeatherForecast
from core.models import WeatherHistory


class ModelRepository:

    def __init__(self, model):
        self.model = model

    def get_all(self) -> QuerySet:
        return self.model.objects.all()

    def get_by_id(self, id: Any | UUID) -> object | None:
        try:
            UUID(str(id))
            return self.model.objects.filter(uuid=id).first()
        except ValueError:
            return self.model.objects.filter(pk=id).first()

    def get_count(self) -> int:
        return self.model.objects.count()

    def get_first(self) -> object | None:
        return self.model.objects.first()

    def get_last(self) -> object | None:
        return self.model.objects.last()

    def get_or_create(self, **kwargs: Dict[str, Any]) -> object | bool:
        return self.model.objects.get_or_create(**kwargs)

    def create(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> list[object] | object:
        if args:
            return self.model.objects.bulk_create(args[0])

        return self.model.objects.create(**kwargs)

    def delete(self, id: int | UUID, soft_delete=True) -> object | None:
        model = self.get_by_id(id)
        if model:
            if soft_delete:
                try:
                    model.deleted = True
                    model.deleted_at = timezone.now()
                    model.save()
                    return model
                except Exception:
                    return None
            else:
                model.delete()
                return model

        return None

    def filter(self, **kwargs: Dict[str, Any]) -> QuerySet:
        return self.model.objects.filter(**kwargs)


class CityModelRepository(ModelRepository):

    def __init__(self):
        super().__init__(City)

    def get_closest(self, latitude: float, longitude: float, max_distance: int | None = None) -> QuerySet:
        """
        Retrieve objects from the model sorted by distance (km) from the given latitude and longitude.
        Method implements Great circle distance formula (GCDF).

        Args:
            latitude (float): Latitude in degrees.
            longitude (float): Longitude in degrees.
            max_distance (int, optional): Maximum distance in kilometers.If provided, only objects within this distance will be included.

        Returns:
            QuerySet: A QuerySet of model objects sorted by distance from the given latitude and longitude.

        Reference:
            https://stackoverflow.com/questions/19703975/django-sort-by-distance#answer-26219292
        """
        EARTH_RADIUS_KM = 6371
        GCDF = f"{EARTH_RADIUS_KM} * acos(least(greatest(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)), -1), 1))"
        distance_query = RawSQL(GCDF, (latitude, longitude, latitude))

        qs = self.model.objects.all().annotate(distance=distance_query).order_by('distance')

        if max_distance is not None:
            return qs.filter(distance__lt=max_distance)

        return qs


CityRepository = CityModelRepository()
UserStatusRepository = ModelRepository(UserStatus)
UserRepository = ModelRepository(User)
WeatherForecastRepository = ModelRepository(WeatherForecast)
WeatherHistoryRepository = ModelRepository(WeatherHistory)
