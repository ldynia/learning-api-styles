from tests.setup import SetupTestCase

from core.models import CityRepository


class CityMutationTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.headers = {
            "Authorization": f"Bearer {self.get_jwt_token_gql()}"
        }

    def test_create_city_mutation(self):
        before_count = CityRepository.get_count()
        query = """
        mutation {
            createCity(data: {
                name: "Copenhagen"
                country: "Denmark"
                region: "Europe"
                timezone: "Europe/Coopenhagen"
                latitude: 11.123456
                longitude: 222.123456
            }) {
                uuid
                name
                country
                region
                timezone
                latitude
                longitude
            }
        }
        """
        response = self.gql.query(query, headers=self.headers)
        after_count = CityRepository.get_count()

        self.assertIsNone(response.errors)
        self.assertGreater(after_count, before_count)

    def test_update_city(self):
        city = CityRepository.get_first()
        query = f"""
        mutation {{
            updateCity(data: {{uuid: "{city.uuid}", name: "Copenhagen"}}) {{
                name
            }}
        }}
        """
        response = self.gql.query(query, headers=self.headers)

        self.assertIsNone(response.errors)

    def test_hard_delete_city(self):
        before_count = CityRepository.get_count()
        city = CityRepository.get_first()
        query = f"""
        mutation {{
            deleteCity(data: {{uuid: "{city.uuid}"}}) {{
                uuid
            }}
        }}
        """
        response = self.gql.query(query, headers=self.headers)
        after_count = CityRepository.get_count()

        self.assertIsNone(response.errors)
        self.assertLess(after_count, before_count)

    # def test_soft_delete_city(self):
    #     city = CityRepository.get_first()
    #     query = f"""
    #     mutation {{
    #         deleteCity(data: {{uuid: "{city.uuid}"}}) {{
    #             uuid
    #         }}
    #     }}
    #     """
    #     response = self.gql.query(query, headers=self.headers)
    #     city = CityRepository.get_first()
    #     self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
    #     self.assertIsNone(response.errors)
