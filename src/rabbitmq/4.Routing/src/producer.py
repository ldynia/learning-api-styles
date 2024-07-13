#!/usr/bin/env python3

import logging
import os
import random
from ssl import create_default_context

from pika import BasicProperties
from pika import BlockingConnection
from pika import ConnectionParameters
from pika import SSLOptions
from pika.credentials import PlainCredentials

from utils import to_bool
from utils import to_json


class RabbitMQProducer:
    broker = os.getenv("RABBITMQ_BROKER")
    channel = None
    connection = None
    exchange = os.getenv("RABBITMQ_EXCHANGE", "logs")
    exchange_type = os.getenv("RABBITMQ_EXCHANGE_TYPE", "direct")
    password = os.getenv("RABBITMQ_PASS")
    properties = BasicProperties(
        content_type='application/json',
        content_encoding='utf-8',
        headers={"version": "1.0.0"}
    )
    routing_key = random.choice(("info", "warning", "error"))
    user = os.getenv("RABBITMQ_USER")
    tls_enable = to_bool(os.getenv("TLS_ENABLE", True))

    def __init__(self):
        self.__connect()
        self.__declare_channel()
        self.__declare_exchange()

    def __connect(self):
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

    def __declare_exchange(self):
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type
        )

    def publish(self, msg: dict):
        self.properties.headers["version"] = msg["version"]
        msg["data"]["message"] = f"{self.routing_key.capitalize()} {msg['data']['message']}"
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=to_json(msg),
            properties=self.properties
        )
        self.disconnect()
        print(f"[x] Sent '{msg}' message to '{self.exchange}' exchange on '{self.routing_key}' routing key.")

    def disconnect(self):
        """Closes the channel and connection to the RabbitMQ broker."""
        if self.channel.is_open:
            self.channel.close()

        if self.connection.is_open:
            self.connection.close()


if __name__ == "__main__":
    debug = to_bool(os.getenv("DEBUG", False))
    if debug:
        logging.basicConfig(level=logging.INFO)

    msg = {
        "data": {
            "message": "Message"
        },
        "version": "1.0.0"
    }
    producer = RabbitMQProducer()
    producer.publish(msg)
