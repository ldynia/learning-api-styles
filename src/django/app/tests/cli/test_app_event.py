import time
import json

from io import StringIO

from django.core.management import call_command

from tests.setup import SetupTestCase


class AppEventCommandTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.payload = json.dumps({
            "type": "dummy_event.created",
            "timestamp": int(time.time()),
            "data": {"echo": "test"}
        })

    def test_app_event_v1_command(self):
        with StringIO() as out:
            call_command("app_event", "--callback-url", "webhook/v1/echo", "--payload", self.payload, stdout=out)
            self.assertIn(self.payload, out.getvalue())

    def test_app_event_v2_command(self):
        with StringIO() as out:
            call_command("app_event", "--callback-url", "webhook/v2/echo", "--payload", self.payload, stdout=out)
            self.assertIn(self.payload, out.getvalue())
