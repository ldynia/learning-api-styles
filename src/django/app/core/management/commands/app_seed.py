from argparse import BooleanOptionalAction
from datetime import datetime

from django.db import connections
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from config.constants import OM_API_YEAR_END
from config.constants import OM_API_YEAR_START
from core.helpers import Validator
from core.models import AdminSeed
from core.models import City
from core.models import CitySeed
from core.models import WeatherForecast
from core.models import WeatherForecastSeed
from core.models import WeatherHistory
from core.models import WeatherHistorySeed


class Command(BaseCommand):
    help = "Command populates application tables with data."

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, default=datetime.today().year, help="Year to populate data with.")
        parser.add_argument("--from-assets", default=False, action=BooleanOptionalAction, help="Load data from fixtures.")

    def handle(self, *args, **options):
        year = options["year"]
        from_assets = options["from_assets"]

        if not Validator().valid_range(year, OM_API_YEAR_START, OM_API_YEAR_END):
            raise CommandError(f"Year {year} is in invalid range! Allowed range is {OM_API_YEAR_START}-{OM_API_YEAR_END}.")

        # self.__truncate_db()
        self.__seed_admin()
        self.__seed_city()
        self.__seed_weather_forecast()
        self.__seed_weather_history(year, from_assets)

    def __truncate_db(self):
        with connections['default'].cursor() as cursor:
            cursor.execute("TRUNCATE weather_city RESTART IDENTITY CASCADE;")

    def __seed_admin(self):
        print(f"Start seeding 'authtoken_token' table.")

        success, error = AdminSeed().seed()
        if not success:
            raise CommandError(error)

        return f"Table 'authtoken_token' has been seeded."

    def __seed_city(self):
        print(f"Start seeding '{City._meta.db_table}' table.")

        success, error = CitySeed().seed()
        if not success:
            raise CommandError(error)

        return f"Table '{City._meta.db_table}' has been seeded."

    def __seed_weather_forecast(self):
        print(f"Start seeding '{WeatherForecast._meta.db_table}' table.")

        success, error = WeatherForecastSeed().seed()
        if not success:
            raise CommandError(error)

        return f"Table '{WeatherForecast._meta.db_table}' has been seeded."

    def __seed_weather_history(self, year, from_assets):
        print(f"Start seeding '{WeatherHistory._meta.db_table}' table.")

        cities = City.objects.all()
        success, error = WeatherHistorySeed(year).seed(cities, from_assets)
        if not success:
            raise CommandError(error)

        return f"Table '{WeatherHistory._meta.db_table}' has been seeded."
