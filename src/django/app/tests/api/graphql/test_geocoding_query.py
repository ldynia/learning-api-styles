from tests.setup import SetupTestCase

from core.models import CityRepository


class GeocodingQueryTestCase(SetupTestCase):

    def setUp(self):
        super().setUp()

    def test_geocoding_city_query(self):
        city = CityRepository.get_first()
        query = f"""
        query getClosestCity{{
            geocoding(data: {{city: "{city.name}"}}) {{
                uuid
                name
                country
                region
                timezone
                latitude
                longitude
            }}
        }}
        """
        response = self.gql.query(query)

        self.assertIsNone(response.errors)

    def test_geocoding_lat_lon_query(self):
        city = CityRepository.get_first()
        query = f"""
        query getClosestCity{{
            geocoding(data: {{latitude: {city.latitude}, longitude: {city.longitude}}}) {{
                uuid
                name
                country
                region
                timezone
                latitude
                longitude
            }}
        }}
        """
        response = self.gql.query(query)

        self.assertIsNone(response.errors)
