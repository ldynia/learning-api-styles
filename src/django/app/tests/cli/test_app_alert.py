from io import StringIO

from django.core.management import call_command

from core.models import CityRepository
from tests.setup import SetupTestCase


class AppAlertCommandTest(SetupTestCase):

    def setUp(self):
        super().setUp()

    def test_app_alert_command(self):
        with StringIO() as out:
            message = "Armageddon!"
            city = CityRepository.get_first()

            call_command("app_alert", city_uuid=str(city.uuid), message=message, stdout=out)

            self.assertIn(message, out.getvalue())
