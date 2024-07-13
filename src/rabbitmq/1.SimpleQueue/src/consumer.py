#!/usr/bin/env python3

import logging
import os
from ssl import create_default_context

from pika import BlockingConnection
from pika import ConnectionParameters
from pika import SSLOptions
from pika.credentials import PlainCredentials

from utils import to_bool


class RabbitMQConsumer:
    broker = os.getenv("RABBITMQ_BROKER")
    channel = None
    connection = None
    password = os.getenv("RABBITMQ_PASS")
    queue = os.getenv("RABBITMQ_QUEUE")
    tls_enable = os.getenv("TLS_ENABLE")
    user = os.getenv("RABBITMQ_USER")

    def __init__(self, tls_enable=True):
        self.__connect(tls_enable)
        self.__declare_channel()
        self.__declare_queue()

    def __connect(self, tls_enable):
        credentials = PlainCredentials(self.user, self.password)
        if tls_enable:
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
        self.channel = self.connection.channel()

    def __declare_queue(self):
        self.channel.queue_declare(queue=self.queue, durable=True, exclusive=False, auto_delete=False)

    def __callback(self, ch, method, properties, msg):
        msg = msg.decode("utf-8")
        print(f"[x] Received '{msg}' message.")

    def consume(self):
        print(f"[*] Waiting for messages from '{self.queue}' queue. To exit press CTRL+C")
        self.channel.basic_consume(queue=self.queue, auto_ack=True, on_message_callback=self.__callback)
        self.channel.start_consuming()


if __name__ == "__main__":
    debug = to_bool(os.getenv("DEBUG", False))
    if debug:
        logging.basicConfig(level=logging.INFO)

    tls_enable = to_bool(os.getenv("TLS_ENABLE", True))
    RabbitMQConsumer(tls_enable).consume()
