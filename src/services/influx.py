# Heapster on Kubernetes 1.0 use Influxdb 0.8.8
from influxdb.influxdb08 import InfluxDBClient
import os

class Influx():

    def __init__(self):
        self.influx_host = os.environ.get('INFLUX_HOST', 'localhost')
        self.influx_port = os.environ.get('INFLUX_PORT', 8086)
        self.influx_user = os.environ.get('INFLUX_USER', 'root')
        self.influx_pwd = os.environ.get('INFLUX_PWD', 'root')
        self.influx_db = os.environ.get('INFLUX_DB', 'k8s')
        self.influx_batch = os.environ.get('INFLUX_BATCH', 100)
        self.sqlite = None
        self.logger = None

    def connect(self):
        try:
            self.logger.info("Connecting to InfluxDB server at " + self.influx_host + ':' + str(self.influx_port) + " (database " + self.influx_db + ")")
            client = InfluxDBClient(self.influx_host, self.influx_port, self.influx_user, self.influx_pwd, self.influx_db)
            # Test connection
            client.query("list series")
            self.client = client
        except:
            message = "Couldn't connect to influxdb"
            self.logger.error(message)
            raise Exception(message)

    def pull(self, serie_name):
        try:
            # Read the most recent records (desc order)
            query = 'select * from "' + serie_name + '" order desc limit ' + str(self.influx_batch)
            result = self.client.query(query)
        except:
            message = "An error occurred trying to pull data from influxdb"
            self.logger.error(message)
            raise Exception(message)
        return result

    def series(self):
        try:
            result = self.client.query('list series')
        except:
            message = "An error occurred trying to pull data from influxdb"
            self.logger.error(message)
            raise Exception(message)
        return result
