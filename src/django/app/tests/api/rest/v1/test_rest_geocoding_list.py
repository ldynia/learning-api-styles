from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_404_NOT_FOUND

from config.base import REST_FRAMEWORK
from core.api.rest.v1 import GeocodingView
from core.helpers.utils import to_bytes
from core.models import CityRepository
from tests.setup import SetupTestCase


class GeocodingTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.view = GeocodingView.as_view()
        self.repository = CityRepository

    def test_geocoding_query_param_city(self):
        query_params = {"city": "Tokyo"}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(to_bytes(query_params["city"]), response.rendered_content)

    def test_geocoding_query_param_city_empty(self):
        query_params = {"city": ""}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_geocoding_query_param_city_not_exist(self):
        query_params = {"city": "xTokyo"}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_geocoding_query_param_lat_lon(self):
        query_params = {"lat": 52.731161, "lon": 15.240524}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(to_bytes("Istanbul"), response.rendered_content)

    def test_geocoding_query_param_lat_lon_empty(self):
        query_params = {"lat": "", "lon": ""}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_geocoding_query_param_lat_lon_invalid(self):

        query_params = {"lat": "ab", "lon": "cd"}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_geocoding_query_param_valid_version(self):

        query_params = {"city": "Tokyo", "version": REST_FRAMEWORK["DEFAULT_VERSION"]}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_geocoding_query_param_invalid_version(self):

        query_params = {"city": "Tokyo", "version": "v3"}
        request = self.factory.get(f"api/geocoding", query_params)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
