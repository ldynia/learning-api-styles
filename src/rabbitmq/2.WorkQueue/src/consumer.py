#!/usr/bin/env python3

import logging
import os
from logging import INFO
from ssl import create_default_context

from pika import BlockingConnection
from pika import ConnectionParameters
from pika import SSLOptions
from pika.credentials import PlainCredentials

from utils import to_bool
from utils import json_to_dict


class RabbitMQConsumer:
    broker = os.getenv("RABBITMQ_BROKER")
    channel = None
    connection = None
    password = os.getenv("RABBITMQ_PASS")
    queue = os.getenv("RABBITMQ_QUEUE", "die")
    user = os.getenv("RABBITMQ_USER")
    tls_enable = to_bool(os.getenv("TLS_ENABLE", True))

    def __init__(self):
        self.__connect()
        self.__declare_channel()
        self.__declare_queue()

    def __connect(self):
        """Establishes a connection to the RabbitMQ broker."""
        credentials = PlainCredentials(self.user, self.password)
        if self.tls_enable:
            port = 5671
            context = create_default_context(cafile="/etc/rabbitmq/ssl/certs/ca_certificate.pem")
            context.load_cert_chain(
                "/etc/rabbitmq/ssl/certs/client_certificate.pem",
                "/etc/rabbitmq/ssl/private/client_key.pem"
            )
            ssl_options = SSLOptions(context)
            params = ConnectionParameters(self.broker, port, ssl_options=ssl_options, credentials=credentials)
        else:
            port = 5672
            params = ConnectionParameters(self.broker, port, credentials=credentials)

        try:
            self.connection = BlockingConnection(params)
        except Exception:
            print(f"Error: Cannot connect to '{self.broker}' host.")
            exit(1)

    def __declare_channel(self):
        """Declares a channel for established connection to the RabbitMQ broker."""
        self.channel = self.connection.channel()

    def __declare_queue(self, durable=True):
        """Declares a queue in the RabbitMQ broker."""
        self.channel.queue_declare(queue=self.queue, durable=durable)

    def __callback(self, channel, method, properties, msg):
        """
        Callback sleeps for n second and after successful acknowledges task.
        Acknowledgement is done manually by using `basic_ack` method of the `channel` object.
        Acknowledgement is delayed by 2 seconds.
        """
        msg = json_to_dict(msg, properties.content_encoding)["data"]["message"]
        print(f"[x] Received '{msg}' message.")
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self):
        """Consumes one message from the RabbitMQ queue."""
        print(f"[*] Waiting for messages from '{self.queue}' queue. To exit press CTRL+C")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue,
            auto_ack=False,
            on_message_callback=self.__callback
        )
        self.channel.start_consuming()

    def disconnect(self):
        """Closes the channel and connection to the RabbitMQ broker."""
        if self.channel.is_open:
            self.channel.close()

        if self.connection.is_open:
            self.connection.close()


if __name__ == "__main__":
    debug = to_bool(os.getenv("DEBUG", False))
    if debug:
        logging.basicConfig(level=INFO)

    consumer = RabbitMQConsumer()
    consumer.consume()
