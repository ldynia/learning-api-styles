import json
import asyncio

from starlette.endpoints import HTTPEndpoint
from sse_starlette.sse import EventSourceResponse
from redis import asyncio as redisasyncio


from config.constants import REDIS_ALERT_DB
from config.constants import REDIS_HOST
from config.constants import REDIS_PORT
from core.helpers.utils import to_str
from core.helpers.utils import to_bytes


class AlertStreamingEndpoint(HTTPEndpoint):
    redis = redisasyncio.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_ALERT_DB)

    async def get(self, request):
        # Subscribe to channels and listen for messages
        pubsub = self.redis.pubsub()

        async def event_publisher(city_uuid):
            await pubsub.subscribe(city_uuid)
            while True and to_bytes(city_uuid) in pubsub.channels:
                message = await pubsub.get_message(ignore_subscribe_messages=False)
                msg = message and message["type"] == "message"
                msg_matches_channel = message and to_str(message["channel"]) == city_uuid
                if msg and msg_matches_channel:
                    yield json.dumps({"message": to_str(message["data"])})
                await asyncio.sleep(1)

        origin_starlette = f"{request.url.scheme}://{request.url.hostname}:{request.url.port - 1}"
        headers = {"Access-Control-Allow-Origin": origin_starlette}

        city_uuid = request.url.query.split("city_uuid=")[1].split("&")[0]
        return EventSourceResponse(event_publisher(city_uuid), headers=headers, ping=3, send_timeout=3)