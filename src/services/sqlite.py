# Heapster on Kubernetes 1.0 use Influxdb 0.8.8
import sqlite3
import os

class Sqlite():

    def __init__(self):
        # This path can't be configured via environment variable
        # because is mounted on the controller.yml path
        self.db_path = '/var/lib/influbbit/influbbit.db'
        self.conn = None
        self.logger = None

    def connect(self):
        try:
            # Connect to Sqlite3 database
            # (if file doesn't exists, it's created on-the-fly)
            conn = sqlite3.connect(self.db_path)
            self.conn = conn

            # Check if database was initialized
            self.check_db_initialized()
        except:
            message = "Couldn't connect to sqlite"
            self.logger.error(message)
            raise Exception(message)

    def check_db_initialized(self):
        query = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='sync';"
        value = self.queryScalar(query)
        if (value == 0):
            # "sync" table doesn't exists, create tables
            query = "CREATE TABLE IF NOT EXISTS sync (serie_name string PRIMARY KEY, last_sync integer);"
            self.execute(query)
            query = "CREATE TABLE IF NOT EXISTS config (global_batch_counter integer);"
            self.execute(query)
            query = "INSERT INTO config (global_batch_counter) VALUES (0);"
            self.execute(query)

    def get_last_sync(self, serie_name):
        query = "SELECT * FROM sync WHERE serie_name = '" + serie_name + "'"
        result = self.queryAll(query)
        if (len(result) == 0):
            # Create record
            query = "INSERT INTO sync SELECT '" + serie_name + "', 0;"
            self.execute(query)

        query = "SELECT last_sync FROM sync WHERE serie_name = '" + serie_name + "'"
        value = self.queryScalar(query)
        return value

    def get_global_batch_counter(self):
        query = "SELECT global_batch_counter FROM config"
        value = self.queryScalar(query)
        return value

    def put_last_sync(self, serie, last_sync):
        query = "UPDATE sync SET last_sync = '" + str(last_sync) + "' WHERE serie_name = '" + serie + "'"
        self.execute(query)

    def put_global_batch_counter(self, global_batch_counter):
        query = "UPDATE config SET global_batch_counter = " + str(global_batch_counter)
        self.execute(query)

    def queryScalar(self, query):
        result = self.queryOne(query)
        value = result[0]
        return value

    def queryOne(self, query):
        result = self.queryAll(query)
        return result[0]

    def queryAll(self, query):
        result = self.execute(query)
        records = result.fetchall()
        return records

    def execute(self, query):
        cursor = self.conn.cursor()
        result = cursor.execute(query)
        self.conn.commit()
        return result