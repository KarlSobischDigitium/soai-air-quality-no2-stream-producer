import os
import time
import copy
from datetime import datetime
import json
import numpy as np
import pandas as pd

import pika
rabbitmq_host = os.getenv("RABBITMQ_HOST")
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
routing_key = os.getenv("RABBITMQ_ROUTING_KEY")
exchange_id = 'amq.topic'
credentials = pika.credentials.PlainCredentials(username=rabbitmq_user, password=rabbitmq_password)
##### rbmq connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbitmq_host,
                              credentials=credentials,
                              connection_attempts=1,
                              retry_delay=1,
                              heartbeat=30,
                              blocked_connection_timeout=30,
                              socket_timeout=30,
                              stack_timeout=30
                              )
)
channel = connection.channel()
channel.exchange_declare(exchange=exchange_id, exchange_type='topic', durable=True)



while True:

    # USE SOAI LIB HERE TO FETCH AIR DATA

    message_object = {
        'text': 'HEY :D'
    }

    message_as_string = json.dumps(message_object)
    channel.basic_publish(exchange=exchange_id, routing_key=routing_key, body=message_as_string)

    print('message sent')
    time.sleep(20)
