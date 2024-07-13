from rest_framework.status import HTTP_200_OK

from core.www import swagger_ws_schema_view
from tests.setup import SetupTestCase


class OpenAPIWsSchemaTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.view = swagger_ws_schema_view

    def test_rest_schema_manualy(self):
        request = self.factory.get("docs/ws/v1/schema/manual")
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_docs_swagger_ui(self):
        request = self.factory.get("docs/ws/v1")
        response = self.view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)
