from rest_framework.status import HTTP_200_OK
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from tests.setup import SetupTestCase


class JWTTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.balacklist_token_view = TokenBlacklistView.as_view()
        self.get_token_view = TokenObtainPairView.as_view()
        self.refresh_token_view = TokenRefreshView.as_view()
        self.verify_token_view = TokenVerifyView.as_view()
        self.obtain_jwt_request = self.factory.post(f"api/jwt/obtain", {
            "username": "admin",
            "password": "admin"
        }, format="json")

    def test_get_jwt_token(self):
        response = self.get_token_view(self.obtain_jwt_request)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_jwt_token(self):
        response = self.get_token_view(self.obtain_jwt_request)
        self.assertEqual(response.status_code, HTTP_200_OK)

        request = self.factory.post(f"api/jwt/refresh", {
            "refresh": response.data["refresh"],
        }, format="json")
        response = self.refresh_token_view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_verify_jwt_token(self):
        response = self.get_token_view(self.obtain_jwt_request)
        self.assertEqual(response.status_code, HTTP_200_OK)

        request = self.factory.post(f"api/jwt/verify", {
            "token": response.data["access"],
        }, format="json")
        response = self.verify_token_view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_revoke_jwt_token(self):
        response = self.get_token_view(self.obtain_jwt_request)
        self.assertEqual(response.status_code, HTTP_200_OK)

        request = self.factory.post(f"api/jwt/revoke", {
            "refresh": response.data["refresh"],
        }, format="json")

        response = self.balacklist_token_view(request)

        self.assertEqual(response.status_code, HTTP_200_OK)
