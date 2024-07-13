from django.core.management import call_command
from django.core.management.base import CommandError

from tests.setup import SetupTestCase


class AppCitiesCommandTest(SetupTestCase):

    def setUp(self):
        super().setUp()

    def test_app_cities_command(self):
        try:
            call_command("app_cities")
        except CommandError:
            return

    def test_app_cities_command_with_flags(self):
        try:
            call_command("app_cities", city="Copenhagen")
        except CommandError:
            return
