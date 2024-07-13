import unittest
from unittest.mock import patch

from consumer import RabbitMQConsumer


class TestRabbitMQConsumer(unittest.TestCase):

    def setUp(self):
        self.consumer = RabbitMQConsumer()

    def tearDown(self):
        if self.consumer.connection.is_open:
            self.consumer.disconnect()

    def test_consume(self):
        with patch.object(self.consumer.channel, "basic_consume") as mock_consume:
            self.consumer.consume()

    def test_connect_tls_disable(self):
        with patch.object(self.consumer.connection, "close") as mock_close:
            self.consumer._RabbitMQConsumer__connect()
            self.assertIsNotNone(self.consumer.channel)
            mock_close.assert_not_called()

    def test_declare_queue(self):
        with patch.object(self.consumer.channel, "queue_declare") as mock_queue_declare:
            self.consumer._RabbitMQConsumer__declare_queue(durable=True)
            self.assertIsNotNone(self.consumer.channel)
            mock_queue_declare.assert_called_once_with(queue=self.consumer.queue, durable=True)

    def test_channel(self):
        self.assertIsNotNone(self.consumer.channel)
        self.assertTrue(self.consumer.channel.is_open)

    def test_disconnect(self):
        self.consumer.disconnect()
        self.assertFalse(self.consumer.connection.is_open)


if __name__ == "__main__":
    unittest.main()
