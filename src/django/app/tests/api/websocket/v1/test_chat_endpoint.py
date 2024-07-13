import os
import ssl
import websockets
from base64 import b64encode
from uuid import uuid4

from asgiref.sync import sync_to_async
from websockets.exceptions import InvalidStatus

from config import to_boolean
from core.helpers.utils import to_bytes
from core.models import CityRepository
from tests.setup import SetupTestCase


class ChatEndpointTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.access_token_b64 = b64encode(to_bytes(self.get_jwt_token_rest())).decode("ascii")
        self.protocol = "wss" if to_boolean(os.environ["TLS_ENABLE"]) else "ws"
        self.ssl = ssl._create_unverified_context() if self.protocol == "wss" else None

    async def test_chat_endpoint_no_token(self):
        city = await sync_to_async(CityRepository.get_first)()
        url = f"{self.protocol}://{self.ws_host}/ws/v1/chat?city_uuid={city.uuid}"

        try:
            async with websockets.connect(url, ssl=self.ssl, origin=self.client_origin) as websocket:
                websocket.recv()
        except InvalidStatus as e:
            self.assertEqual(403, e.response.status_code)

    async def test_chat_endpoint_with_wrong_uuid(self):
        url = f"{self.protocol}://{self.ws_host}/ws/v1/chat?city_uuid={uuid4()}&access_token={self.access_token_b64}"

        async with websockets.connect(url, ssl=self.ssl, origin=self.client_origin) as websocket:
            try:
                await websocket.recv()
            except Exception:
                self.assertIn("doesn't exist", websocket.close_reason)
                self.assertEqual(1008, websocket.close_code)

    async def test_chat_endpoint_without_uuid(self):
        url = f"{self.protocol}://{self.ws_host}/ws/v1/chat?access_token={self.access_token_b64}"

        async with websockets.connect(url, ssl=self.ssl, origin=self.client_origin) as websocket:
            try:
                await websocket.recv()
            except Exception:
                self.assertIn("city_uuid is missing", websocket.close_reason)
                self.assertEqual(1008, websocket.close_code)
