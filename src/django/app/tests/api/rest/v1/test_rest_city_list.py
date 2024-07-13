from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_201_CREATED
from rest_framework.status import HTTP_404_NOT_FOUND

from config.base import REST_FRAMEWORK
from core.api.rest.v1 import CityListView
from core.models import CityRepository
from tests.setup import SetupTestCase


class CityListTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.get_jwt_token_rest()}",
        }
        self.repository = CityRepository
        self.view = CityListView.as_view()

    def test_city_list_get(self):
        request = self.factory.get("api/cities", **self.headers)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertGreater(len(response.rendered_content), 2)

    def test_city_list_get_query_param_valid(self):
        query_params = {"fields": "name,uuid", "version": REST_FRAMEWORK["DEFAULT_VERSION"]}
        request = self.factory.get("api/cities", query_params, **self.headers)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertGreater(len(response.rendered_content), 2)

    def test_city_list_get_query_params_invalid(self):
        query_params = {"fields": "name,uuid", "version": "v3"}
        request = self.factory.get("api/cities", query_params, **self.headers)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertGreater(len(response.rendered_content), 2)

    def test_city_list_post(self):
        hometown = "Gorzów Wielkopolski"
        request = self.factory.post("api/cities", {
            "name": hometown,
            "country": "Poland",
            "region": "Europe",
            "timezone": "Europe/Gorzow Wielkopolski",
            "latitude": 52.731161,
            "longitude": 15.240524
        }, format="json", **self.headers)
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        city = self.repository.filter(name=hometown).first()
        self.assertIsNotNone(city)
