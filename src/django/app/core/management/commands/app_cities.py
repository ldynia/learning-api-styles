from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from core.models import CityRepository


class Command(BaseCommand):
    help = "Command prints city name, id, and uuid"

    def add_arguments(self, parser):
        parser.add_argument("--city", type=str, default="", help="City name to search for.")

    def handle(self, *args, **options):
        city_name = options["city"]
        if city_name:
            city = CityRepository.filter(name__icontains=city_name).first()
            if not city:
                raise CommandError("City not found.")

            return f"{city.name} {city.uuid}"

        cities = CityRepository.get_all().order_by("name")
        if not cities:
            raise CommandError("No cities in the database")

        output = ""
        for city in cities:
            output += f"{city.name} {city.uuid}\n"

        return output
