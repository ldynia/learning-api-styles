import time

from datetime import datetime
from datetime import timezone

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.test import RequestFactory
from standardwebhooks import Webhook

from config.constants import WEBHOOK_SECRET_B64
from core.api.webhook.v2.views import WebhookCustomView
from core.api.webhook.v1.views import WebhookStandardView


class Command(BaseCommand):
    help = "Command simulates source service sending webhook events to the destination service."
    wh = Webhook(WEBHOOK_SECRET_B64)

    def add_arguments(self, parser):
        parser.add_argument("--callback-url", type=str, default="webhook/v1/echo", help="Webhooks destination URI")
        parser.add_argument("--msg-id", type=str, default="123abc", help="Webhook msg id.")
        parser.add_argument("--payload", type=str, help="JSON encoded payload.")

    def handle(self, *args, **options):
        endpoint = options["callback_url"]
        msg_id = options["msg_id"]
        payload = options["payload"]
        timestamp = datetime.fromtimestamp(time.time(), tz=timezone.utc)

        if endpoint not in ["webhook/v1/echo", "webhook/v2/echo"]:
            raise CommandError(f"Invalid endpoint {endpoint}")

        if endpoint == "webhook/v1/echo":
            return self.__webhook_v1(endpoint, timestamp, payload, msg_id)

        return self.__webhook_v2(endpoint, timestamp, payload, msg_id)

    def __webhook_v1(self, endpoint: str, timestamp: datetime, payload: str, msg_id: str):
        signature = self.wh.sign(msg_id, timestamp, payload)

        headers = {
            "Webhook-Id": msg_id,
            "Webhook-Signature": signature,
            "Webhook-Timestamp": timestamp.timestamp(),
        }

        factory = RequestFactory()
        request = factory.post(endpoint, payload, headers=headers, content_type='application/json')

        view = WebhookStandardView.as_view()
        response = view(request)

        return f'POST {endpoint} \n{response.content.decode("utf-8")}'

    def __webhook_v2(self, endpoint: str, timestamp: datetime, payload: str, msg_id: str):
        signature = self.wh.sign(msg_id, timestamp, payload)

        headers = {
            "Webhook-Id": msg_id,
            "Webhook-Signature": signature,
            "Webhook-Timestamp": timestamp.timestamp(),
        }

        factory = RequestFactory()
        request = factory.post(endpoint, payload, headers=headers, content_type='application/json')
        view = WebhookCustomView.as_view()

        response = view(request)

        return f'POST {endpoint} \n{response.content.decode("utf-8")}'
