import json
import time

from datetime import datetime
from datetime import timezone

from rest_framework.status import HTTP_200_OK
from standardwebhooks import Webhook

from config.constants import WEBHOOK_SECRET_B64
from tests.setup import SetupTestCase


class WebhookEchoSecuredTestCase(SetupTestCase):

    def test_webhook_echo_secure_endpoint(self):
        id = "123abc"
        timestamp = datetime.fromtimestamp(time.time(), tz=timezone.utc)
        payload = json.dumps({
            "type": "dummy_event.created",
            "timestamp": int(timestamp.timestamp()),
            "data": {"echo": "test"}
        })

        signature = Webhook(WEBHOOK_SECRET_B64).sign(id, timestamp, payload)

        headers = {
            "Webhook-ID": id,
            "Webhook-Signature": signature,
            "Webhook-Timestamp": int(timestamp.timestamp())
        }
        response = self.client.post("/webhook/v2/echo", payload, content_type="application/json", headers=headers)
        response_data = response.content.decode("utf-8")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(payload, response_data)
