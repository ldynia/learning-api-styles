#!/usr/bin/env python

import logging
import os
from ssl import create_default_context

from pika import BasicProperties
from pika import BlockingConnection
from pika import ConnectionParameters
from pika import SSLOptions
from pika.credentials import PlainCredentials

from utils import to_bool


class Server:
    broker = os.getenv("RABBITMQ_BROKER", "broker")
    channel = None
    connection = None
    password = os.getenv("RABBITMQ_PASS")
    request_queue = os.getenv("RABBITMQ_QUEUE", "factorial")
    user = os.getenv("RABBITMQ_USER")
    tls_enable = to_bool(os.getenv("TLS_ENABLE", True))

    def __init__(self):
        self.__connect()
        self.__declare_channel()
        self.__declare_request_queue()

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
        self.channel = self.connection.channel()

    def __declare_request_queue(self):
        self.channel.queue_declare(queue=self.request_queue)

    def __on_request(self, channel, method, props, body):
        n = int(body)
        reply_queue = props.reply_to
        correlation_id = props.correlation_id
        result = str(self.factorial(n))
        delivery_tag = method.delivery_tag
        print(f"[.] Computing factorial({n}) for correlation id {correlation_id} response sent to {reply_queue} queue.")

        # Create response message
        channel.basic_publish(
            exchange="",
            routing_key=reply_queue,
            properties=BasicProperties(correlation_id=correlation_id),
            body=result
        )
        channel.basic_ack(delivery_tag=delivery_tag)

    def factorial(self, n):
        if n == 0:
            return 1
        return n * self.factorial(n - 1)

    def consume(self):
        print(f"[x] Awaiting messages from '{self.request_queue}' queue. To exit press CTRL+C")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.request_queue,
            on_message_callback=self.__on_request
        )
        self.channel.start_consuming()


if __name__ == "__main__":
    debug = to_bool(os.getenv("DEBUG", False))
    if debug:
        logging.basicConfig(level=logging.INFO)

    server = Server()
    server.consume()
