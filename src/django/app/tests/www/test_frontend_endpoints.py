from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from core.api.atom.views import WeatherForecastFeedListView
from core.models import CityRepository
from core.www import root_view
from tests.setup import SetupTestCase


class WWWEndpointsTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.view = root_view
        self.repository = CityRepository
        self.forecast_view = WeatherForecastFeedListView.as_view()

    def test_root_www(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(b"Weather Forecast Service API", response.content)

    def test_alert_www(self):
        response = self.client.get("/websocket/alert")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(b"Weather Forecast Service Alert", response.content)

    def test_echo_www(self):
        response = self.client.get("/websocket/echo")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(b"Echo WebSocket Application", response.content)

    def test_chat_www(self):
        response = self.client.get("/websocket/chat")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(b"Weather Forecast Service Chat", response.content)

    def test_forecast_uuid(self):
        city = self.repository.get_first()
        response = self.client.get(reverse("city_forecast", args=[city.uuid]))

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(b"Weather Forecast Service", response.content)

    def test_atom_feed(self):
        response = self.client.get(reverse("city_feed"))

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(b'xmlns="http://www.w3.org/2005/Atom"', response.content)
