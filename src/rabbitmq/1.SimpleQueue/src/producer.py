#!/usr/bin/env python3

import logging
import os
import random
import time

from pika import BlockingConnection
from pika import ConnectionParameters
from pika import SSLOptions
from pika.credentials import PlainCredentials
from pika.exceptions import UnroutableError
from pika.spec import BasicProperties
from pika.spec import TRANSIENT_DELIVERY_MODE
from ssl import create_default_context

from utils import to_bool


class RabbitMQProducer:
    broker = os.getenv("RABBITMQ_BROKER")
    channel = None
    connection = None
    exchange = ""
    password = os.getenv("RABBITMQ_PASS")
    queue = os.getenv("RABBITMQ_QUEUE")
    user = os.getenv("RABBITMQ_USER")

    def __init__(self, tls_enable=True):
        self.__connect(tls_enable)
        self.__declare_channel()
        self.__declare_queue()
        # Enable publisher confirms
        self.channel.confirm_delivery()

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

    def publish(self, msg: str, max_retries=3):
        attempts = 0
        message = msg.encode()
        while attempts < max_retries:
            try:
                self.channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.queue,
                    body=msg,
                    properties=BasicProperties(delivery_mode=TRANSIENT_DELIVERY_MODE),
                    mandatory=True  # The message will be returned if it cannot be routed
                )
                # If we get here, the broker confirmed the message
                print(f"[x] Sent '{message}' message to '{self.queue}' queue and received confirmation.")
                break
            except UnroutableError:
                attempts += 1
                print(f"[!] Message was rejected by the broker as unroutable (attempt {attempts}/{max_retries})")
                if attempts >= max_retries:
                    print("[!] Failed to publish message after maximum retries")
                    break
                time.sleep(attempts * max_retries)
            except Exception as e:
                attempts += 1
                print(f"[!] Failed to publish message: {e} (attempt {attempts}/{max_retries})")
                if attempts >= max_retries:
                    print("[!] Failed to publish message after maximum retries")
                    break
                time.sleep(attempts * max_retries)


if __name__ == "__main__":
    debug = to_bool(os.getenv("DEBUG", False))
    if debug:
        logging.basicConfig(level=logging.INFO)

    tls_enable = to_bool(os.getenv("TLS_ENABLE", True))
    message = f"Rolling {random.randrange(1, 6)}"
    producer = RabbitMQProducer(tls_enable)
    producer.publish(message)
