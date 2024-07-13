from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from redis import asyncio

from config.constants import REDIS_ALERT_DB
from config.constants import REDIS_HOST
from config.constants import REDIS_PORT
from core.helpers import Validator
from core.models import CityRepository


class Command(BaseCommand):
    city = CityRepository.get_first()
    help = "Command sends alert message to channel identified by city's uuid."
    redis = asyncio.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_ALERT_DB)

    def add_arguments(self, parser):
        parser.add_argument("--city-uuid", type=str, default=f"{self.city.uuid}", help="City's uuid.")
        parser.add_argument("--message", type=str, default="Hail storm is coming!", help="Alert message.")

    @async_to_sync
    async def handle(self, *args, **options):
        city_uuid = options["city_uuid"]
        if city_uuid:
            if not Validator().valid_uuid(city_uuid):
                raise CommandError(f"City uuid '{city_uuid}' is not valid!")

            city = await sync_to_async(CityRepository.get_by_id)(city_uuid)
            if not city:
                raise CommandError(f"City with uuid '{city_uuid}' does not exist!")

        message = options["message"]
        await self.redis.publish(city_uuid, message)
        await self.redis.close()

        return f"Alert '{message}' sent to '{city_uuid}' channel."
