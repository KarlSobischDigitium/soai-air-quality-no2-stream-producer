import os
import time
import copy
from datetime import datetime
import json
import numpy as np
import pandas as pd
import pika
import time
import os
import json
import simplejson
import logging
from lib.SOIADataFetcherService import SOIADataFetcherService


rabbitmq_host = os.getenv("RABBITMQ_HOST")
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
routing_key = 'soai.data.no2'
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

    print('Enter loop')

    service = SOIADataFetcherService()
    service.update_sensor_setwork()

    data = service.fetch_data()

    print(data)

    message_as_string = json.dumps(data)
    channel.basic_publish(exchange=exchange_id, routing_key=routing_key, body=message_as_string)

    print('message sent')
    time.sleep(10)
