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
from lib.ExamplePublisher import ExamplePublisher


rabbitmq_host = os.getenv("RABBITMQ_HOST")
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
routing_key = 'soai.data.no2'
exchange_id = 'amq.topic'

url = "amqp://{}:{}@{}:5672/%2F?connection_attempts=10&heartbeat=3600"\
        .format(rabbitmq_user, rabbitmq_password, rabbitmq_host)

example_publisher = ExamplePublisher(url, routing_key, exchange_id)

example_publisher.run()

