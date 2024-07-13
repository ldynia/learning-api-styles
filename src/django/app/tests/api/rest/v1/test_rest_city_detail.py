from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_412_PRECONDITION_FAILED

from config.base import REST_FRAMEWORK
from core.api.rest.v1 import CityView
from core.helpers.utils import to_bytes
from core.models import CityRepository
from tests.setup import SetupTestCase


class CityDetailTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.get_jwt_token_rest()}",
        }
        self.repository = CityRepository
        self.view = CityView.as_view()

    def test_city_detail_get(self):
        city = self.repository.get_first()
        query_params = {"fields": "name,uuid"}
        request = self.factory.get(f"api/cities/{city.uuid}", query_params, **self.headers)
        response = self.view(request, city.uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn(to_bytes(str(city.uuid)), response.rendered_content)

    def test_city_detail_get_query_param_valid_version(self):
        city = self.repository.get_first()
        query_params = {"version": REST_FRAMEWORK["DEFAULT_VERSION"]}
        request = self.factory.get(f"api/cities/{city.uuid}", query_params, **self.headers)
        response = self.view(request, city.uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_city_detail_get_query_param_invalid_version(self):
        city = self.repository.get_first()
        query_params = {"version": "v3"}
        request = self.factory.get(f"api/cities/{city.uuid}", query_params, **self.headers)
        response = self.view(request, city.uuid)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_city_detail_patch(self):
        city = self.repository.get_first()
        city_name_reversed = city.name[::-1]

        data = {"name": city_name_reversed}
        request = self.factory.patch(f"api/cities/{city.uuid}", data, format="json", **self.headers)
        response = self.view(request, city.uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        city = self.repository.get_by_id(city.uuid)
        self.assertEqual(city.name, city_name_reversed)

    def test_city_detail_put(self):
        city = self.repository.get_first()
        city_name = city.name

        request = self.factory.put(f"api/cities/{city.uuid}", {
            "name": city.name.upper(),
            "country": city.country.upper(),
            "region": city.region.upper(),
            "timezone": city.timezone.upper(),
            "latitude": city.latitude,
            "longitude": city.longitude
        }, format="json", **self.headers)
        response = self.view(request, city.uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        city = self.repository.get_by_id(city.uuid)
        self.assertEqual(city.name, city_name.upper())

    def test_city_detail_put_with_errors(self):
        first_city = self.repository.get_first()
        last_city = self.repository.get_last()

        request = self.factory.put(f"api/cities/{last_city.uuid}", {
            "name": last_city.name,
            "country": first_city.country,
            "region": first_city.region,
            "timezone": first_city.timezone,
            "latitude": first_city.latitude,
            "longitude": first_city.longitude
        }, format="json", **self.headers)
        response = self.view(request, first_city.uuid)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_city_detail_soft_delete(self):
        city = self.repository.get_first()
        request = self.factory.delete(f"api/cities/{city.uuid}", **self.headers)
        response = self.view(request, city.uuid)

        city = self.repository.get_by_id(city.uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(city.deleted)

    def test_city_detail_double_soft_delete(self):
        city = self.repository.get_first()

        request = self.factory.delete(f"api/cities/{city.uuid}", **self.headers)
        response = self.view(request, city.uuid)

        city = self.repository.get_by_id(city.uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(city.deleted)

        request = self.factory.delete(f"api/cities/{city.uuid}", **self.headers)
        response = self.view(request, city.uuid)

        self.assertEqual(response.status_code, HTTP_412_PRECONDITION_FAILED)
        self.assertTrue(city.deleted)

    def test_city_detail_hard_delete(self):
        city = self.repository.get_first()
        request = self.factory.delete(f"api/cities/{city.uuid}?soft_delete=false", **self.headers)
        response = self.view(request, city.uuid)

        city = self.repository.get_by_id(city.uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsNone(city)

    def test_city_detail_double_hard_delete(self):
        city_uuid = self.repository.get_first().uuid

        request = self.factory.delete(f"api/cities/{city_uuid}?soft_delete=false", **self.headers)
        response = self.view(request, city_uuid)

        city = self.repository.get_by_id(city_uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsNone(city)

        request = self.factory.delete(f"api/cities/{city_uuid}?soft_delete=false", **self.headers)
        response = self.view(request, city_uuid)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertIsNone(city)

    def test_city_soft_delete_folloed_by_hard_delete(self):
        city_uuid = self.repository.get_first().uuid

        request = self.factory.delete(f"api/cities/{city_uuid}?soft_delete=true", **self.headers)
        response = self.view(request, city_uuid)

        city = self.repository.get_by_id(city_uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(city.deleted)

        request = self.factory.delete(f"api/cities/{city_uuid}?soft_delete=false", **self.headers)
        response = self.view(request, city_uuid)

        city = self.repository.get_by_id(city_uuid)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsNone(city)

        request = self.factory.delete(f"api/cities/{city_uuid}?soft_delete=false", **self.headers)
        response = self.view(request, city_uuid)

        city = self.repository.get_by_id(city_uuid)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertIsNone(city)

    def test_city_hard_delete_folloed_by_soft_delete(self):
        city_uuid = self.repository.get_first().uuid

        request = self.factory.delete(f"api/cities/{city_uuid}?soft_delete=false", **self.headers)
        response = self.view(request, city_uuid)

        city = self.repository.get_by_id(city_uuid)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIsNone(city)

        request = self.factory.delete(f"api/cities/{city_uuid}?soft_delete=true", **self.headers)
        response = self.view(request, city_uuid)

        city = self.repository.get_by_id(city_uuid)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertIsNone(city)
