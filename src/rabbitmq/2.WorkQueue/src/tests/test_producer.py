import unittest
from unittest.mock import patch

from producer import RabbitMQProducer


class TestRabbitMQProducer(unittest.TestCase):

    def setUp(self):
        self.producer = RabbitMQProducer()

    def tearDown(self):
        self.producer.disconnect()

    def test_publish(self):
        with patch.object(self.producer.channel, "basic_publish") as mock_publish:
            msg = {"data": {"message": "Hello, world!"}, "version": "1.0.0"}
            self.producer.publish(msg)
            mock_publish.assert_called_once_with(
                exchange="",
                routing_key=self.producer.queue,
                body='{"data": {"message": "Hello, world!"}, "version": "1.0.0"}',
                properties=self.producer.properties
            )

    def test_connect_tls_disable(self):
        with patch.object(self.producer.connection, "close") as mock_close:
            self.producer._RabbitMQProducer__connect()
            self.assertIsNotNone(self.producer.channel)
            mock_close.assert_not_called()

    def test_declare_queue(self):
        with patch.object(self.producer.channel, "queue_declare") as mock_queue_declare:
            self.producer._RabbitMQProducer__declare_queue(durable=True)
            self.assertIsNotNone(self.producer.channel)
            mock_queue_declare.assert_called_once_with(queue=self.producer.queue, durable=True)

    def test_channel(self):
        self.assertIsNotNone(self.producer.channel)
        self.assertTrue(self.producer.channel.is_open)

    def test_disconnect(self):
        self.producer.disconnect()
        self.assertFalse(self.producer.connection.is_open)


if __name__ == "__main__":
    unittest.main()
