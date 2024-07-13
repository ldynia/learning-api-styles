import json
import os

from config import to_boolean
from tests.setup import SetupTestCase


class EchoEndpointTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.protocol = "wss" if to_boolean(os.environ["TLS_ENABLE"]) else "ws"

    def test_echo_ws(self):
        url = f"{self.protocol}://{self.ws_host}/ws/v1/echo"
        self.stc.headers = {"Origin": self.client_origin}
        with self.stc.websocket_connect(url) as websocket:
            data = {"message": "hello"}
            json_str = json.dumps(data)

            websocket.send_json(json_str)
            response = websocket.receive_json()

            self.assertIn(data["message"], response)
