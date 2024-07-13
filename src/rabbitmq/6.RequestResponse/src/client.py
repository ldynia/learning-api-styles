#!/usr/bin/env python

import logging
import os
import random
import uuid
from ssl import create_default_context

from pika import BasicProperties
from pika import BlockingConnection
from pika import ConnectionParameters
from pika import SSLOptions
from pika.credentials import PlainCredentials

from utils import to_bool


class Client:
    broker = os.getenv("RABBITMQ_BROKER", "broker")
    channel = None
    connection = None
    corr_id = str(uuid.uuid4())
    password = os.getenv("RABBITMQ_PASS")
    reply_queue = ""
    request_queue = os.getenv("RABBITMQ_QUEUE", "factorial")
    response = None
    user = os.getenv("RABBITMQ_USER")
    tls_enable = to_bool(os.getenv("TLS_ENABLE", True))

    def __init__(self):
        self.__connect()
        self.__declare_channel()
        self.__declare_reply_queue()
        self.__consume_reply_queue()

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

    def __declare_reply_queue(self):
        queue = self.channel.queue_declare(queue="", exclusive=True)
        self.reply_queue = queue.method.queue

    def __consume_reply_queue(self):
        self.channel.basic_consume(
            queue=self.reply_queue,
            on_message_callback=self.__on_response,
            auto_ack=True
        )

    def __on_response(self, channel, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        # Create request message
        self.channel.basic_publish(
            exchange="",
            routing_key=self.request_queue,
            properties=BasicProperties(
                reply_to=self.reply_queue,
                correlation_id=self.corr_id
            ),
            body=str(n)
        )

        # Infinite loop that awaits response
        while self.response is None:
            self.connection.process_data_events()

        print(f"[x] Calling factorial({n}) = {int(self.response)} with correlation id {self.corr_id} reply queue is {self.reply_queue}")
        return int(self.response)


if __name__ == "__main__":
    debug = to_bool(os.getenv("DEBUG", False))
    if debug:
        logging.basicConfig(level=logging.INFO)

    number = random.randint(0, 10)
    client = Client()
    client.call(number)
