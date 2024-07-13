from typing import Any
from typing import Dict
from uuid import UUID

from rest_framework.serializers import CharField
from rest_framework.serializers import DecimalField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ReadOnlyField
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from core.models import City
from core.models import WeatherForecast
from core.models import WeatherHistory


class DynamicFieldsModelSerializer(ModelSerializer):
    """
    Serializer takes `fields` argument that controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don"t pass "fields" arg to superclass.
        fields = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)

        # Remove fields that are not specified in the `fields` argument.
        if fields is not None:
            allowed_fields = set(fields)
            existing_fields = set(self.fields)
            for field in existing_fields - allowed_fields:
                self.fields.pop(field)


class CitySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = City
        fields = [
            "uuid",
            "name",
            "country",
            "region",
            "timezone",
            "latitude",
            "longitude",
            "deleted",
        ]
        # Make city name unique
        validators = [UniqueTogetherValidator(queryset=City.objects.all(), fields=["name"])]

    uuid = ReadOnlyField()
    name = CharField(read_only=False, required=True, max_length=255)
    country = CharField(read_only=False, required=True, allow_blank=False, max_length=225)
    region = CharField(read_only=False, required=True, max_length=255)
    timezone = CharField(read_only=False, required=True, max_length=255)
    latitude = DecimalField(read_only=False, required=True, max_digits=8, decimal_places=6)
    longitude = DecimalField(read_only=False, required=True, max_digits=9, decimal_places=6)

    def create(self, data: Dict[str, Any]) -> City:
        return City.objects.create(**data)

    def update(self, instance: City, data: Dict[str, Any]):
        instance.name = data.get("name", instance.name)
        instance.country = data.get("country", instance.country)
        instance.region = data.get("region", instance.region)
        instance.timezone = data.get("timezone", instance.timezone)
        instance.latitude = data.get("latitude", instance.latitude)
        instance.longitude = data.get("longitude", instance.longitude)
        instance.save()
        return instance


class WeatherForecastSerializer(DynamicFieldsModelSerializer):
    city_name = SerializerMethodField()
    city_uuid = SerializerMethodField()

    class Meta:
        model = WeatherForecast
        fields = [
            "city_name",
            "city_uuid",
            "date",
            "rain_sum_mm",
            "showers_sum_mm",
            "snowfall_sum_cm",
            "sunrise_iso8601",
            "sunset_iso8601",
            "temperature_max_celsius",
            "temperature_min_celsius",
            "uv_index_max",
            "wind_speed_max_kmh",
        ]

    def get_city_uuid(self, obj: object) -> UUID:
        return obj.city.uuid

    def get_city_name(self, obj: object) -> str:
        return obj.city.name


class WeatherHistorySerializer(DynamicFieldsModelSerializer):
    city_name = SerializerMethodField()
    city_uuid = SerializerMethodField()

    class Meta:
        model = WeatherHistory
        fields = [
            "city_name",
            "city_uuid",
            "date",
            "rain_sum_mm",
            "snowfall_sum_cm",
            "sunrise_iso8601",
            "sunset_iso8601",
            "temperature_max_celsius",
            "temperature_min_celsius",
            "wind_speed_max_kmh",
        ]

    def get_city_uuid(self, obj: object) -> UUID:
        return obj.city.uuid

    def get_city_name(self, obj: object) -> str:
        return obj.city.name
