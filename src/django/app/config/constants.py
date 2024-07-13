from datetime import datetime
from datetime import timedelta

from config.base import *


FIRST = 0
LAST = -1

APP_DEFAULT_YEAR = datetime.now().year
APP_FORECAST_DAYS_MAX = 7
APP_FORECAST_DAYS_MIN = 1
APP_STARLETTE_AUTHENTICATE_ENDPOINTS = set(["/ws/v1/alert", "/ws/v1/chat", "/sse/v1/alert"])
APP_WEBSOCKET_ENCODING = "json"

ASSETS_API_REST_SCHEMA = f"{BASE_DIR}/docs/api/rest"
ASSETS_API_WS_SCHEMA = f"{BASE_DIR}/docs/api/websocket"
ASSETS_DB_CITIES = f"{BASE_DIR}/assets/db/fixtures/weather_city.json"
ASSETS_DB_FORECAST = f"{BASE_DIR}/assets/db/fixtures/weather_forecast.json"
ASSETS_DB_HISTORY = f"{BASE_DIR}/assets/db/fixtures/weather_history.json"
ASSETS_DEPENDENCIES_PIP_MODULES = f"{BASE_DIR}/requirements.txt"

# https://open-meteo.com/en/docs
OM_API_ARCHIVE_ENDPOINT = "https://archive-api.open-meteo.com/v1/archive"
OM_API_CALL_TIMEOUT_SECONDS = 3
OM_API_FORECAST_ENDPOINT = "https://api.open-meteo.com/v1/forecast"
OM_API_YEAR_START = 1940
OM_API_YEAR_END = datetime.now().year
OM_API_DATE_END = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")
OM_API_DATE_START = f"{OM_API_YEAR_START}-01-01"

WS_1008_POLICY_VIOLATION = 1008

DOCS = {
    "city": {
        "uuid": "City's unique identifier.",
        "name": "City's name.",
        "country": "Holding country.",
        "region": "Holding region.",
        "timezone": "City's timezone.",
        "latitude": "City's latitude.",
        "longitude": "City's longitude.",
        "deleted": "Soft delete flag.",
        "deleted_at": "The times that a resource was soft deleted.",
        "purge_at": "The time when a soft deleted resource will be purged from the system.",
        "created_at": "Creation timestamp.",
        "updated_at": "Update timestamp.",
    },
    "forecast": {
        "date": "Forecast date.",
        "rain_sum_mm": "Sum of daily rain in mm.",
        "showers_sum_mm": "Sum of daily showers in mm.",
        "snowfall_sum_cm": "Sum of daily snowfall in cm.",
        "sunrise_iso8601": "Sunrise time iso8601 formatted.",
        "sunset_iso8601": "Sunset time iso8601 formatted.",
        "temperature_max_celsius": "Max temperature at 2m in Celsius.",
        "temperature_min_celsius": "Min temperature at 2m in Celsius.",
        "uv_index_max": "UV index daily maximum.",
        "wind_speed_max_kmh": "Maximum wind speed and gusts on a day at 10m in kmh.",
        "created_at": "Creation timestamp.",
        "updated_at": "Update timestamp.",
    },
    "history": {
        "date": "Weather at this date.",
        "rain_sum_mm": "Sum of daily rain in mm.",
        "snowfall_sum_cm": "Sum of daily snowfall in cm.",
        "sunrise_iso8601": "Sunrise time iso8601 formatted.",
        "sunset_iso8601": "Sunset time iso8601 formatted.",
        "temperature_max_celsius": "Max temperature at 2m in Celsius.",
        "temperature_min_celsius": "Min temperature at 2m in Celsius.",
        "wind_speed_max_kmh": "Maximum wind speed and gusts on a day at 10m in kmh.",
        "created_at": "Creation timestamp.",
        "updated_at": "Update timestamp.",
    },
    "errors": {
        "creation_failed": "Failed to create {0} object.",
        "delete_failed": "Failed to delete {0} object.",
        "filter_failed": "Failed to filter {0} object.",
        "not_exist": "Referenced {0} ({1}) does not exist.",
        "not_found": "Referenced {0} ({1}) not found.",
        "not_superuser": "Only superuser can perform this operation.",
        "read_failed": "Failed to read from {0} database.",
        "soft_delete": "Referenced {0} ({1}) is already soft deleted.",
        "update_failed": "Failed to update {0}({1}) object.",
    },
    "query": {
        "cities": "Return a list of cities.",
        "forecast": "City's weather forecasts.",
        "geocoding": "City look-up based on coordinates or city name.",
        "history": "City's weather history.",
    },
    "mutation": {
        "create_city": "Create city.",
        "delete_city": "Delete city.",
        "seed_all_city": "Seed cities with historical weather data.",
        "seed_city": "Seed city with historical weather data.",
        "update_city": "Update city.",
    },
    "input": {
        "geocoding": "Provide city's name or latitude and longitude. If all inputs are present, then city takes precedence over latitude and longitude.",
        "forecast": "Weather forecast input.",
        "seed": "Weather seed input.",
    },
    "input_field": {
        "city": "City's name.",
        "latitude": "City's latitude.",
        "longitude": "City's longitude.",
        "city_uuid": "City's unique identifier.",
        "country": "Holding country.",
        "region": "Holding country.",
        "timezone": "City's timezone.",
    },
    "order": {
        "city": "City's sorting fields.",
        "history": "Weather history sorting fields.",
        "forecast": "Weather forecast sorting fields.",
    },
}
