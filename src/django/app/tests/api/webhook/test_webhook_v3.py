import json

from rest_framework.status import HTTP_200_OK

from tests.setup import SetupTestCase


class WebhookEchoTestCase(SetupTestCase):

    def test_webhook_echo_endpoint(self):
        data = {"webhook": "works"}
        response = self.client.post("/webhook/v3/echo", data, content_type="application/json")
        response_data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(data, response_data)
