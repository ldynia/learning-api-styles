#!/usr/bin/env python3

import logging
import os
import random
from ssl import create_default_context
from logging import INFO

from pika import BasicProperties
from pika import BlockingConnection
from pika import ConnectionParameters
from pika import SSLOptions
from pika.credentials import PlainCredentials
from pika.spec import PERSISTENT_DELIVERY_MODE

from utils import to_bool
from utils import to_json


class RabbitMQProducer:
    broker = os.getenv("RABBITMQ_BROKER")
    channel = None
    connection = None
    password = os.getenv("RABBITMQ_PASS")
    properties = BasicProperties(
        content_type='application/json',
        content_encoding='utf-8',
        delivery_mode=PERSISTENT_DELIVERY_MODE,
        headers={"version": "1.0.0"}
    )
    queue = os.getenv("RABBITMQ_QUEUE", "die")
    user = os.getenv("RABBITMQ_USER")
    tls_enable = to_bool(os.getenv("TLS_ENABLE", True))

    def __init__(self):
        """Create a connection and declare a queue."""
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

    def publish(self, msg: dict):
        """Publishes a message to the RabbitMQ queue."""
        self.properties.headers["version"] = msg["version"]
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=to_json(msg),
            properties=self.properties
        )
        self.disconnect()
        print(f"[x] Sent '{msg}' message to '{self.queue}' queue.")

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

    number = random.randrange(1, 6)
    msg = {
        "data": {
            "message": f"Rolling {number}",
            "outcome": number
        },
        "version": "1.0.0"
    }

    producer = RabbitMQProducer()
    producer.publish(msg)
