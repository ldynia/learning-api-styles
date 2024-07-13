import unittest

from client import Client


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_call(self):
        resp = self.client.call(5)
        self.assertEqual(resp, 120)
