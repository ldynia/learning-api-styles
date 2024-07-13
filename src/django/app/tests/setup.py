import os

from django.test import Client as DjangoTestClient
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase
from starlette.testclient import TestClient as StarletteTestClient
from strawberry_django.test.client import TestClient as StrawberryTestClient

from config.asgi import application_starlette
from config.constants import APP_DEFAULT_YEAR
from core.models import AdminSeed
from core.models import CityRepository
from core.models import CitySeed
from core.models import UserRepository
from core.models import WeatherForecastSeed
from core.models import WeatherHistorySeed


class SetupTestCase(APITestCase):
    """Setup class for all unitest classes."""

    def setUp(self):
        self.admin = UserRepository.filter(username='admin').first()
        self.client = DjangoTestClient()
        self.client_origin = "localhost:8000"
        self.factory = APIRequestFactory()
        self.gql = StrawberryTestClient('/graphql')
        self.stc = StarletteTestClient(application_starlette)
        self.ws_host = f"localhost:{os.getenv('APP_PORT_WS', '8001')}"

    @classmethod
    def setUpTestData(cls):
        cls.__seed_admin()
        cls.__seed_city()
        cls.__seed_forecast()
        cls.__seed_history()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    @classmethod
    def __seed_admin(cls) -> None:
        AdminSeed().seed()

    @classmethod
    def __seed_city(cls) -> None:
        CitySeed().seed()

    @classmethod
    def __seed_forecast(cls) -> None:
        WeatherForecastSeed().seed()

    @classmethod
    def __seed_history(cls) -> None:
        from_assets = True
        cities = CityRepository.get_all()
        WeatherHistorySeed(APP_DEFAULT_YEAR).seed(cities, from_assets)

    def get_jwt_token_rest(self) -> str:
        request = self.factory.post(f'api/jwt/obtain', {
            'username': 'admin',
            'password': 'admin'
        }, format='json')

        response = TokenObtainPairView.as_view()(request)
        if response.status_code == HTTP_200_OK:
            return response.data['access']

        return ""

    def get_jwt_token_gql(self) -> str:
        query = """
        mutation {
            obtainJwt(username: "admin", password: "admin") {
                token {
                   token
                }
            }
        }
        """
        request = self.gql.query(query)
        if not request.errors:
            return request.data['obtainJwt']['token']['token']

        return ""
