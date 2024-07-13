import json
import time

from datetime import datetime
from datetime import timezone

from standardwebhooks import Webhook
from rest_framework.status import HTTP_200_OK

from config.constants import WEBHOOK_SECRET_B64
from tests.setup import SetupTestCase


class WebhookStandardTestCase(SetupTestCase):

    def test_standard_webhook_echo_endpoint(self):
        id = "123abc"
        timestamp = datetime.fromtimestamp(time.time(), tz=timezone.utc)
        payload = json.dumps({
            "type": "dummy_event.created",
            "timestamp": int(timestamp.timestamp()),
            "data": {"echo": "test"}
        })

        signature = Webhook(WEBHOOK_SECRET_B64).sign(id, timestamp, payload)

        headers = {
            "Webhook-Id": id,
            "Webhook-Signature": signature,
            "Webhook-Timestamp": int(timestamp.timestamp()),
        }

        response = self.client.post("/webhook/v1/echo", payload, content_type="application/json", headers=headers)
        response_data = response.content.decode("utf-8")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(payload, response_data)
