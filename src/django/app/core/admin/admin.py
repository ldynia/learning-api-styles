from django.contrib.admin import ModelAdmin
from django.contrib.admin import site as admin_site

from core.models import City
from core.models import WeatherHistory
from core.models import WeatherForecast


class CityAdmin(ModelAdmin):
    list_display = ["id", "uuid", "name", "country", "created_at", "updated_at"]
    list_display_links = ["id", "uuid"]
    ordering = ["id"]


class WeatherForecastAdmin(ModelAdmin):
    list_display = ["id", "city", "date", "created_at", "updated_at"]
    list_select_related = True
    ordering = ["id"]


class WeatherHistoryAdmin(ModelAdmin):
    list_display = ["id", "city", "date", "created_at", "updated_at"]
    list_select_related = True
    ordering = ["id"]


admin_site.register(City, CityAdmin)
admin_site.register(WeatherForecast, WeatherForecastAdmin)
admin_site.register(WeatherHistory, WeatherHistoryAdmin)
