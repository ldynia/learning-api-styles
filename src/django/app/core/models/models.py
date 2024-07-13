from uuid import uuid4

from django.db.models import BooleanField
from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import DateField
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import FloatField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import UUIDField

from config.constants import DOCS


class City(Model):

    class Meta:
        db_table = "weather_city"
        verbose_name_plural = "Cities"

    uuid = UUIDField(primary_key=False, unique=True, default=uuid4, editable=False, help_text=DOCS["city"]["uuid"])
    name = CharField(blank=False, null=False, max_length=255, help_text=DOCS["city"]["name"])
    country = CharField(blank=False, null=False, max_length=255, help_text=DOCS["city"]["country"])
    region = CharField(blank=False, null=False, max_length=255, help_text=DOCS["city"]["region"])
    timezone = CharField(blank=False, null=False, max_length=255, help_text=DOCS["city"]["timezone"])
    latitude = FloatField(blank=False, null=False, help_text=DOCS["city"]["latitude"])
    longitude = FloatField(blank=False, null=False, help_text=DOCS["city"]["longitude"])
    deleted = BooleanField(default=False, help_text=DOCS["city"]["deleted"])
    deleted_at = DateTimeField(blank=True, null=True, help_text=DOCS["city"]["deleted_at"])
    purge_at = DateTimeField(blank=True, null=True, help_text=DOCS["city"]["purge_at"])
    created_at = DateTimeField(auto_now_add=True, help_text=DOCS["city"]["created_at"])
    updated_at = DateTimeField(auto_now=True, help_text=DOCS["city"]["updated_at"])

    def __str__(self):
        return f'{self.name}'


class WeatherForecast(Model):

    class Meta():
        db_table = "weather_forecast"
        verbose_name_plural = "Weather Forecasts"
        ordering = ["date"]

    city = ForeignKey(City, on_delete=CASCADE, related_name="forecast")
    date = DateField(blank=False, null=False, help_text=DOCS["forecast"]["date"])
    rain_sum_mm = DecimalField(default=0, max_digits=4, decimal_places=1, help_text=DOCS["forecast"]["rain_sum_mm"])
    showers_sum_mm = DecimalField(default=0, max_digits=4, decimal_places=1, help_text=DOCS["forecast"]["showers_sum_mm"])
    snowfall_sum_cm = DecimalField(default=0, max_digits=4, decimal_places=1, help_text=DOCS["forecast"]["snowfall_sum_cm"])
    sunrise_iso8601 = DateTimeField(help_text=DOCS["forecast"]["sunrise_iso8601"])
    sunset_iso8601 = DateTimeField(help_text=DOCS["forecast"]["sunset_iso8601"])
    temperature_max_celsius = DecimalField(default=0, max_digits=3, decimal_places=1, help_text=DOCS["forecast"]["temperature_max_celsius"])
    temperature_min_celsius = DecimalField(default=0, max_digits=3, decimal_places=1, help_text=DOCS["forecast"]["temperature_min_celsius"])
    uv_index_max = DecimalField(default=0, max_digits=3, decimal_places=2, help_text=DOCS["forecast"]["uv_index_max"])
    wind_speed_max_kmh = DecimalField(default=0, max_digits=4, decimal_places=1, help_text=DOCS["forecast"]["wind_speed_max_kmh"])
    created_at = DateTimeField(auto_now_add=True, help_text=DOCS["forecast"]["created_at"])
    updated_at = DateTimeField(auto_now=True, help_text=DOCS["forecast"]["updated_at"])


class WeatherHistory(Model):

    class Meta():
        db_table = "weather_history"
        verbose_name_plural = "Weather History"

    city = ForeignKey(City, on_delete=CASCADE, related_name="history")
    date = DateField(blank=False, null=False, help_text=DOCS["history"]["date"])
    rain_sum_mm = DecimalField(default=0, max_digits=4, decimal_places=1, help_text=DOCS["history"]["rain_sum_mm"])
    snowfall_sum_cm = DecimalField(default=0, max_digits=4, decimal_places=1, help_text=DOCS["history"]["snowfall_sum_cm"])
    sunrise_iso8601 = DateTimeField(help_text=DOCS["history"]["sunrise_iso8601"])
    sunset_iso8601 = DateTimeField(help_text=DOCS["history"]["sunset_iso8601"])
    temperature_max_celsius = DecimalField(default=0, max_digits=3, decimal_places=1, help_text=DOCS["history"]["temperature_max_celsius"])
    temperature_min_celsius = DecimalField(default=0, max_digits=3, decimal_places=1, help_text=DOCS["history"]["temperature_min_celsius"])
    wind_speed_max_kmh = DecimalField(default=0, max_digits=4, decimal_places=1, help_text=DOCS["history"]["wind_speed_max_kmh"])
    created_at = DateTimeField(auto_now_add=True, help_text=DOCS["history"]["created_at"])
    updated_at = DateTimeField(auto_now=True, help_text=DOCS["history"]["updated_at"])
