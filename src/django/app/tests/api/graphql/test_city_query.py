from tests.setup import SetupTestCase

from core.models import CityRepository


class CityQueryTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()

    def test_city_filtering_query(self):
        city = CityRepository.get_first()
        query = f"""
        query getCityByNameLatLon {{
            cities(
                filters: {{
                    name: {{ iContains: "{city.name}" }}
                    latitude: {{ exact: {city.latitude} }}
                    longitude: {{ exact: {city.longitude} }}
                }}
            ) {{
                uuid
                name
            }}
        }}
        """
        response = self.gql.query(query)

        self.assertIsNone(response.errors)

    def test_city_ordering_query(self):
        query = """
        query getCities {
            cities(order: {name: DESC}) {
                name
                country
                country
                timezone
                latitude
                longitude
            }
        }
        """
        response = self.gql.query(query)

        self.assertIsNone(response.errors)