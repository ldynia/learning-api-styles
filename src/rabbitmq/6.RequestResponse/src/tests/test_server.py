import unittest

from server import Server


class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = Server()

    def test_factorial(self):
        self.assertEqual(self.server.factorial(0), 1)
        self.assertEqual(self.server.factorial(1), 1)
        self.assertEqual(self.server.factorial(2), 2)
        self.assertEqual(self.server.factorial(3), 6)
        self.assertEqual(self.server.factorial(4), 24)
        self.assertEqual(self.server.factorial(5), 120)
