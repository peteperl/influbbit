# See http://www.rabbitmq.com/tutorials/tutorial-one-python.html
import pika
import json
import os

class Rabbit():

    def __init__(self):
        # CLUSTER_IP and RABBIT_HOST are mandatory as env variables
        self.cluster_ip = os.environ.get('CLUSTER_IP')
        self.rabbit_host = os.environ.get('RABBIT_HOST')

        self.cluster_name = os.environ.get('CLUSTER_NAME', 'kubernetes')
        self.rabbit_port = int(os.environ.get('RABBIT_PORT', 5672))
        self.rabbit_vhost = os.environ.get('RABBIT_VHOST', '/')
        self.rabbit_user = os.environ.get('RABBIT_USER', 'guest')
        self.rabbit_pwd = os.environ.get('RABBIT_PWD', 'guest')
        self.rabbit_queue = os.environ.get('RABBIT_QUEUE', 'test_q')
        self.rabbit_exchange = os.environ.get('RABBIT_EXCHANGE', 'test_exchange')
        self.rabbit_batch = os.environ.get('RABBIT_BATCH', 100)

        # Number of items on the current batch
        self.batch_counter = 0

        # Global counter of batches, even across services restarts
        self.global_batch_counter = 0

        self.batch_content = dict()
        self.sqlite = None
        self.logger = None

    def connect(self):
        try:
            self.logger.info("Connecting to RabbitMQ server at " + self.rabbit_host + ':' + str(self.rabbit_port) + " (queue " + self.rabbit_queue + ")")
            credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_pwd)
            parameters = pika.ConnectionParameters(self.rabbit_host, self.rabbit_port, self.rabbit_vhost, credentials)
            self.connection = pika.BlockingConnection(parameters)
            self.global_batch_counter = int(self.sqlite.get_global_batch_counter())
        except:
            message = "Couldn't connect to rabbitmq"
            self.logger.error(message)
            raise Exception(message)

    def push(self, serie_name, data):
        last_sync = self.sqlite.get_last_sync(serie_name)
        # self.logger.debug("Last sync on database for serie " + serie_name + " is " + str(last_sync))
        new_records = 0
        for record in data:
            columns = record['columns']
            points = record['points']
            # Data is queried in descending order (from most recent, last X items)
            # but we use reversed to push that info using an ascending order to the queue
            for point in reversed(points):
                # First item is the unix epoch time
                point_time = point[0]
                if point_time > last_sync:
                    try:
                        new_records += 1
                        self.batch_counter += 1

                        combined = { 'serie': serie_name, 'columns': columns, 'info': point}
                        serialized = json.dumps(combined)
                        self.batch_content[self.batch_counter] = serialized
                        self.sqlite.put_last_sync(serie_name, point_time)

                        if int(self.batch_counter) == int(self.rabbit_batch):
                            # Send batch
                            self.global_batch_counter += 1
                            # self.logger.debug("Reached " + str(self.batch_counter) + " items on the batch. Sending to RabbitMQ...")
                            item = dict([('cluster_name', self.cluster_name), ('cluster_ip', self.cluster_ip), ('batch_number', self.global_batch_counter), ('data', self.batch_content)])
                            serializedItem = json.dumps(item)
                            channel = self.connection.channel()
                            channel.basic_publish(exchange=self.rabbit_exchange, routing_key=self.rabbit_queue, body=serializedItem)
                            self.logger.info("New batch of " + str(self.batch_counter) + " InfluxDB records was sent in a RabbitMQ item")
                            self.batch_counter = 0
                            self.batch_content = dict()
                            self.sqlite.put_global_batch_counter(self.global_batch_counter)
                    except:
                        message = "An error occurred trying to push data to rabbitmq"
                        self.logger.error(message)
                        raise Exception(message)

        return new_records
