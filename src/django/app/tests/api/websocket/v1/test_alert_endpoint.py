import json
import os
import ssl
import websockets

from asgiref.sync import sync_to_async
from base64 import b64encode
from ssl import _create_unverified_context
from uuid import uuid4
from websockets.exceptions import InvalidStatus

from django.core.management import call_command

from config import to_boolean
from core.helpers.utils import to_bytes
from core.models import CityRepository
from tests.setup import SetupTestCase


class AlertEndpointTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.city = CityRepository.get_first()
        self.protocol = "wss" if to_boolean(os.environ["TLS_ENABLE"]) else "ws"
        self.ssl = ssl._create_unverified_context() if self.protocol == "wss" else None
        self.access_token_b64 = b64encode(to_bytes(self.get_jwt_token_rest())).decode("ascii")

    async def test_alert_endpoint_no_token(self):
        url = f"{self.protocol}://{self.ws_host}/ws/v1/alert?city_uuid={self.city.uuid}"
        try:
            async with websockets.connect(url, ssl=self.ssl, origin=self.client_origin) as websocket:
                websocket.recv()
        except InvalidStatus as e:
            self.assertEqual(403, e.response.status_code)

    async def test_alert_endpoint_with_wrong_uuid(self):
        url = f"{self.protocol}://{self.ws_host}/ws/v1/alert?city_uuid={uuid4()}&access_token={self.access_token_b64}"
        async with websockets.connect(url, ssl=self.ssl, origin=self.client_origin) as websocket:
            try:
                await websocket.recv()
            except Exception:
                self.assertIn("doesn't exist", websocket.close_reason)
                self.assertEqual(1008, websocket.close_code)

    # Leave this code for future testing!
    # async def test_alert_endpoint(self):
    #     message = "Alert works!"
    #     url = f"{self.protocol}://{self.ws_host}/ws/v1/alert?city_uuid={self.city.uuid}&access_token={self.access_token_b64}"

    #     async with websockets.connect(url, ssl=self.ssl, origin=self.client_origin) as websocket:
    #         await sync_to_async(call_command)("app_alert", city_uuid=str(self.city.uuid), message=message)

    #         response = await websocket.recv()
    #         response = json.loads(response)

    #         # TODO This should pass but, it's not the case!
    #         self.assertIn(message, response["message"])
