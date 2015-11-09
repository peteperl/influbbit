# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python influbbit.py start

# Standard python libs
import logging
import time
import os

# Third party libs
from daemon import runner
from services.influx import Influx
from services.rabbit import Rabbit
from services.sqlite import Sqlite

class App():
   
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/influx-rabbit/influx-rabbit.pid'
        self.pidfile_timeout = 5
        self.run_as_daemon = False
        self.logger = None
        self.idle_wait_secs = os.environ.get('IDLE_WAIT_SECS', 10)
           
    def run(self):
        logger.info("Starting Influbbit service")

        # Initialize services

        # Initialize Sqlite
        sqlite = Sqlite()
        sqlite.logger = self.logger
        sqlite.connect()
        logger.info("Connected to Sqlite")

        # Initialize Influxdb
        influx = Influx()
        influx.logger = self.logger
        influx.sqlite = sqlite
        influx.connect()
        logger.info("Connected to Influxdb")

        # Initialize Rabbitmq
        rabbit = Rabbit()
        rabbit.logger = self.logger
        rabbit.sqlite = sqlite
        rabbit.connect()
        logger.info("Connected to Rabbitmq")

        logger.info("Influbbit service initialized")

        stop = False
        seriesList = influx.series()
        series = seriesList[0]['points']
        while not stop:
            new_records = 0
            for serie in series:
                serie_name=serie[1]
                logger.debug("Checking new data for serie " + serie_name + "...")
                data = influx.pull(serie_name)
                if len(data) != 0:
                    # logger.debug("Obtained " + str(len(data)) + " records, checking if were already sent...")
                    new_records += rabbit.push(serie_name, data)

            if (new_records == 0):
                # No data on last read. Wait before read again
                self.logger.info("New data not found. Waiting " + str(self.idle_wait_secs) + " seconds ...")
                time.sleep(float(int(self.idle_wait_secs)))

# Configure Logger
logger = logging.getLogger("DaemonLog")
debug_mode = os.environ.get('DEBUG_MODE', 0)
if (debug_mode == 0):
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

# Configure Application
app = App()
if app.run_as_daemon:
    handler = logging.FileHandler("/var/log/influbbit/influbbit.log")
else:
    handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
app.logger = logger

# Set run mode (foreground or background)
if app.run_as_daemon:
    # Run in background as daemon
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve=[handler.stream]
    daemon_runner.do_action()
else:
    # Run on foreground (Docker-Way)
    app.run()