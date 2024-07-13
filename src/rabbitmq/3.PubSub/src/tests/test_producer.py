import unittest
from unittest.mock import patch

from producer import RabbitMQProducer


class TestRabbitMQProducer(unittest.TestCase):

    def setUp(self):
        self.producer = RabbitMQProducer()

    def tearDown(self):
        self.producer.disconnect()

    def test_connect_tls_enable(self):
        with patch.object(self.producer.connection, "close") as mock_close:
            self.producer._RabbitMQProducer__connect()
            self.assertIsNotNone(self.producer.connection)
            mock_close.assert_not_called()

    def test_connect_tls_disable(self):
        with patch.object(self.producer.connection, "close") as mock_close:
            self.producer._RabbitMQProducer__connect()
            self.assertIsNotNone(self.producer.connection)
            mock_close.assert_not_called()

    def test_channel(self):
        self.assertIsNotNone(self.producer.channel)
        self.assertTrue(self.producer.channel.is_open)

    def test_declare_exchange(self):
        with patch.object(self.producer.channel, "exchange_declare") as mock_declare:
            self.producer._RabbitMQProducer__declare_exchange()
            mock_declare.assert_called_once_with(
                exchange=self.producer.exchange,
                exchange_type=self.producer.exchange_type
            )

    def test_publish(self):
        with patch.object(self.producer.channel, "basic_publish") as mock_publish:
            msg = {"version": "1.0", "data": "test message"}
            self.producer.publish(msg)
            mock_publish.assert_called_once_with(
                exchange=self.producer.exchange,
                routing_key="",
                body='{"version": "1.0", "data": "test message"}',
                properties=self.producer.properties
            )

    def test_disconnect(self):
        self.producer.disconnect()
        self.assertFalse(self.producer.channel.is_open)


if __name__ == "__main__":
    unittest.main()
