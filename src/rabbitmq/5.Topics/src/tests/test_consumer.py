import unittest
from unittest.mock import MagicMock, patch

from consumer import RabbitMQConsumer


class TestRabbitMQConsumer(unittest.TestCase):

    def setUp(self):
        self.consumer = RabbitMQConsumer()

    def tearDown(self):
        self.consumer.disconnect()

    def test_connect_tls_enable(self):
        with patch.object(self.consumer.connection, "close") as mock_close:
            self.consumer._RabbitMQConsumer__connect()
            self.assertIsNotNone(self.consumer.connection)
            mock_close.assert_not_called()

    def test_connect_tls_disable(self):
        with patch.object(self.consumer.connection, "close") as mock_close:
            self.consumer._RabbitMQConsumer__connect()
            self.assertIsNotNone(self.consumer.connection)
            mock_close.assert_not_called()

    def test_channel(self):
        self.assertIsNotNone(self.consumer.channel)
        self.assertTrue(self.consumer.channel.is_open)

    def test_queue(self):
        self.assertIsNotNone(self.consumer.queue)

    def test_declare_exchange(self):
        with patch.object(self.consumer.channel, "exchange_declare") as mock_declare:
            self.consumer._RabbitMQConsumer__declare_exchange()
            mock_declare.assert_called_once_with(
                exchange=self.consumer.exchange,
                exchange_type=self.consumer.exchange_type
            )

    def test_callback(self):
        with patch("builtins.print") as mock_print:
            msg = b'{"data": {"message": "Test message"}, "version": "1.0.0"}'
            properties = MagicMock(content_encoding="utf-8")
            self.consumer._RabbitMQConsumer__callback(None, None, properties, msg)

    def test_consume(self):
        with patch.object(self.consumer.channel, "basic_consume") as mock_consume:
            self.consumer.consume()
            mock_consume.assert_called_once_with(
                queue=self.consumer.queue,
                auto_ack=True,
                on_message_callback=self.consumer._RabbitMQConsumer__callback
            )

    def test_disconnect(self):
        self.consumer.disconnect()
        self.assertFalse(self.consumer.connection.is_open)
