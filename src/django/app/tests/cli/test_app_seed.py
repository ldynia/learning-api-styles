from django.core.management import call_command

from core.models import WeatherHistoryRepository
from tests.setup import SetupTestCase


class AppSeedCommandTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.repository = WeatherHistoryRepository

    def test_app_seed_command(self):
        before_count = self.repository.get_all().count()

        call_command("app_seed", year=1984)

        after_count = self.repository.get_all().count()

        self.assertGreater(after_count, before_count)

    def test_app_seed_from_assets_command(self):
        before_count = self.repository.get_all().count()

        call_command("app_seed", from_assets=True)

        after_count = self.repository.get_all().count()

        self.assertGreaterEqual(after_count, before_count)
