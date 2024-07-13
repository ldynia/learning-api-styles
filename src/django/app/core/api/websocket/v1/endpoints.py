import asyncio

from asgiref.sync import sync_to_async
from redis import asyncio as redisasyncio
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket
from typing import Any
from typing import Dict

from config.constants import APP_WEBSOCKET_ENCODING
from config.constants import REDIS_ALERT_DB
from config.constants import REDIS_HOST
from config.constants import REDIS_PORT
from config.constants import WS_1008_POLICY_VIOLATION
from core.helpers.utils import to_bytes
from core.helpers.utils import to_str
from core.models import CityRepository


class AlertEndpoint(WebSocketEndpoint):
    clients = dict()
    encoding = APP_WEBSOCKET_ENCODING
    lock = asyncio.Lock()
    pubsub = redisasyncio.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_ALERT_DB).pubsub()

    async def on_connect(self, websocket: WebSocket):
        """
        When new WebSocket is connect to the server this function creates a pubsub channel from the city_uuid.
        Then adds WebSocket connection to the clients dictionary, which binds WebSockets clients with Redi's pubsub channel.
        Finally, it creates a task to watch the messages coming from pubsub channel and send these messages to the connected WebSockets.

        Args:
            websocket: The WebSocket instance that initiated the connection.
        """
        await websocket.accept()
        city_uuid = websocket.query_params.get("city_uuid")
        if not city_uuid:
            reason = "Query parameter city_uuid is missing or is invalid."
            return await websocket.close(code=WS_1008_POLICY_VIOLATION, reason=reason)

        city = await sync_to_async(CityRepository.get_by_id)(city_uuid)
        if not city:
            reason = f"City with {city_uuid} doesn't exist."
            return await websocket.close(code=WS_1008_POLICY_VIOLATION, reason=reason)

        # Subscribes to channels and listens for new messages
        await self.pubsub.subscribe(city_uuid)

        # Create dictionary to hold ws connections
        if city_uuid not in self.clients:
            self.clients[city_uuid] = set()
        self.clients[city_uuid].add(websocket)

        # Create a task to watch pubsub channel and send these messages to the connected WebSockets
        asyncio.create_task(self.__msg_watch_and_broadcast(websocket, city_uuid))

    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        """
        When WebSocket client is disconnected from the server function removes disconected WebSocket from the channels.
        """
        city_uuid = websocket.query_params.get("city_uuid")
        clients = self.clients.get(city_uuid)
        if city_uuid and clients:
            for client in clients.copy():
                if websocket == client:
                    self.clients[city_uuid].remove(client)

    async def __msg_watch_and_broadcast(self, websocket: WebSocket, city_uuid: str):
        """
        This async coroutine watches the messages coming from pubsub channel and send these messages to the connected WebSockets.
        Coroutine is locked with asyncio.Lock to prevent multiple coroutines from accessing it concurrently.
        Finally, reading of messages is done with intervals of 1 seconds.

        Args:
            websocket: The WebSocket instance that initiated the connection.
            city_uuid: The name of the channel to watch for messages.
        """
        while to_bytes(city_uuid) in self.pubsub.channels:
            async with self.lock:
                message = await self.pubsub.get_message(ignore_subscribe_messages=False)
                msg = message and message["type"] == "message"
                msg_matches_channel = message and to_str(message["channel"]) == city_uuid
                if msg and msg_matches_channel:
                    data = {"message": to_str(message["data"])}
                    await self.__broadcast(city_uuid, data)
            await asyncio.sleep(1)

    async def __broadcast(self, city_uuid: str, data: Dict[str, Any],):
        """
        Broadcasts data to all connected WebSockets clients in a specified city_uuid.
        If 'skip_sender' is True then omit the sender.

        Args:
            city_uuid: The name of the city_uuid to broadcast the message to.
            data: The data to be sent as a message to the connected WebSockets.
        """
        for client in self.clients.get(city_uuid).copy():
            try:
                await client.send_json(data)
            except Exception as e:
                print(f"Failed to send message due to {e}")


class ChatEndpoint(WebSocketEndpoint):
    clients = dict()
    encoding = APP_WEBSOCKET_ENCODING

    async def on_connect(self, websocket: WebSocket):
        """
        When new client is connect to the server this function adds WebSocket connection to the clients dictionary,
        to keep track of active WebSockets clients for a given city.
        """
        await websocket.accept()
        city_uuid = websocket.query_params.get("city_uuid")
        if not city_uuid:
            reason = "Query parameter city_uuid is missing or is invalid."
            return await websocket.close(code=WS_1008_POLICY_VIOLATION, reason=reason)
        try:
            city = await sync_to_async(CityRepository.get_by_id)(city_uuid)
        except Exception:
            city = None

        if not city:
            reason = f"City with {city_uuid} doesn't exist."
            return await websocket.close(code=WS_1008_POLICY_VIOLATION, reason=reason)
        else:
            data = {"message": f"Welcome in {city.name} chat."}
            await websocket.send_json(data)

        # Create city's empty channel to hold ws connections
        if city_uuid not in self.clients:
            self.clients[city_uuid] = set()

        # Add WebSocket to the channel
        self.clients[city_uuid].add(websocket)

    async def on_receive(self, websocket: WebSocket, data: Any):
        """Broadcasts data to all connected WebSockets in a specified channel (city_uuid)."""
        city_uuid = websocket.query_params.get("city_uuid")
        if city_uuid:
            data = {"message": data.get("message")}
            await self.__broadcast(city_uuid, data, websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        """Remove disconnected WebSocket from the clients."""
        city_uuid = websocket.query_params.get("city_uuid")
        clients = self.clients.get(city_uuid)
        if city_uuid and clients:
            for client in clients.copy():
                if websocket == client:
                    self.clients[city_uuid].remove(client)

    async def __broadcast(self, city_uuid: str, data: Dict[str, Any], sender: WebSocket, skip_sender: str = False):
        """
        Broadcasts data to all connected WebSockets for a specified city.
        If 'skip_sender' is True then omit the sender.

        Args:
            city_uuid: The name of the city_uuid to broadcast the message to.
            data: The data to be sent as a message to the connected WebSockets.
            sender: The WebSocket instance that initiated the message.
            skip_sender: If True, the message won't be sent to the sender. Default is False.
        """
        for client in self.clients.get(city_uuid):
            # Prevent sending message to original sender of the message
            if skip_sender and sender == client:
                continue

            try:
                await client.send_json(data)
            except Exception as e:
                print(f"Failed to send message due to {e}")


class EchoEndpoint(WebSocketEndpoint):
    encoding = APP_WEBSOCKET_ENCODING

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: Any):
        await websocket.send_json(data)
