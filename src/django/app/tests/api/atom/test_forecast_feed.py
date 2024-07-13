from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from tests.setup import SetupTestCase


class CityAtomFeedTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()

    def test_atom_feed(self):
        response = self.client.get(reverse("city_feed"))

        self.assertEqual(response.status_code, HTTP_200_OK)
