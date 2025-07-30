from uuid import UUID

import strawberry
from gqlauth.user import arg_mutations
from strawberry_django import field
from strawberry_django.mutations import create
from strawberry_django.mutations import delete
from strawberry_django.mutations import update
from strawberry.types import Info

from .inputs import CityInput
from .inputs import CityInputPartial
from .inputs import SeedInput
from .inputs import UUIDInput
from .normalizers import normalize_city_input
from .types import CityType
from config.constants import DOCS
from config.constants import ENVIRONMENT
from core.helpers import CitySerializer
from core.helpers import get_serializer_errors
from core.helpers import InputDataHandler
from core.helpers import InputDataValidator
from core.helpers import IsAdmin
from core.helpers import IsAuthenticated
from core.models import CityRepository
from core.models import WeatherHistorySeed


@strawberry.type
class CityMutation:
    create_city: CityType = create(CityInput, permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["create_city"])
    update_city: CityType = update(CityInputPartial, key_attr="uuid", permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["update_city"])
    delete_city: CityType = delete(UUIDInput, key_attr="uuid", permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["delete_city"])


@strawberry.type
class CustomCityMutation:

    @field(permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["create_city"])
    def create_city(self, info: Info, data: CityInput) -> CityType:
        data = normalize_city_input(data)

        serializer = CitySerializer(data=data)
        if not serializer.is_valid():
            errors = get_serializer_errors(serializer)
            if errors:
                raise Exception(errors[0])

        try:
            return serializer.save()
        except Exception:
            raise Exception(DOCS["errors"]["create_failed"].format("City"))

    @field(permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["update_city"])
    def update_city(self, info: Info, data: CityInputPartial) -> CityType:
        city = CityRepository.get_by_id(data.uuid)
        if not city:
            raise Exception(DOCS["errors"]["not_found"].format("City", data.uuid))

        data = normalize_city_input(data)

        serializer = CitySerializer(city, data=data, partial=True)
        if not serializer.is_valid():
            errors = get_serializer_errors(serializer)
            if errors:
                raise Exception(errors[0])
        try:
            return serializer.save()
        except Exception:
            raise Exception(DOCS["errors"]["update_failed"].format("City", data.uuid))

    @field(permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["delete_city"])
    def delete_city(self, info: Info, data: UUIDInput) -> CityType:
        try:
            city = CityRepository.get_by_id(data.uuid)
        except Exception:
            raise Exception([DOCS["errors"]["read_failed"].format("City")])

        if not city:
            raise Exception(DOCS["errors"]["not_found"].format("City", data.uuid))

        city = CityRepository.delete(city.uuid, not data.soft_delete)
        if not city:
            return Exception([DOCS["errors"]["delete_failed"].format("City")])

        return city
    

@strawberry.type
class WeatherHistoryMutation:

    @field(permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["seed_all_city"])
    def seed_all_cities_weather_history(self, info: Info, data: SeedInput) -> bool:
        # Validate input data
        year, errors = InputDataHandler(InputDataValidator, request=False).handle_year(data)
        if errors:
            return Exception(errors[0])

        try:
            cities = CityRepository.get_all()
        except Exception:
            return Exception(DOCS["errors"]["read_failed"].format("City"))

        # Seed weather history for all cities
        seeded, err = WeatherHistorySeed(year).seed(cities, False)
        if not seeded:
            return Exception(err)

        return True

    @field(permission_classes=[IsAuthenticated, IsAdmin], description=DOCS["mutation"]["seed_city"])
    def seed_city_weather_history(self, info: Info, uuid: UUID, data: SeedInput) -> bool:
        # Validate input data
        year, errors = InputDataHandler(InputDataValidator, request=False).handle_year(data)
        if errors:
            return Exception(errors[0])

        # Validate city
        try:
            city = CityRepository.get_by_id(uuid)
        except Exception:
            return Exception(DOCS["errors"]["read_failed"].format("City"))

        if not city:
            raise Exception(DOCS["errors"]["not_found"].format("City", uuid))

        # Seed weather history
        seeded, err = WeatherHistorySeed(year).seed([city], False)
        if not seeded:
            return Exception(err)

        return True


@strawberry.type
class JWTMutation:
    # Strawbery Django Auth Mutations
    obtain_jwt = arg_mutations.ObtainJSONWebToken.field
    refresh_jwt = arg_mutations.RefreshToken.field
    revoke_jwt = arg_mutations.RevokeToken.field
    verify_jwt = arg_mutations.VerifyToken.field


if ENVIRONMENT == "development":
    @strawberry.type
    class Mutation(CityMutation, JWTMutation, WeatherHistoryMutation):
        pass
    @strawberry.type
    class CustomMutation(CustomCityMutation, JWTMutation, WeatherHistoryMutation):
        pass
else:
    @strawberry.type
    class Mutation(CityMutation, JWTMutation):
        pass
    @strawberry.type
    class CustomMutation(CustomCityMutation, JWTMutation):
        pass
