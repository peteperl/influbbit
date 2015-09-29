# Influbbit
#### Coming soon...

### Kubernetes stat collection 

Service to export stats from one or more Kubernetes clusters to a central repository for viewing and analysis. 

The goal is to include this as a service to Kubernetes [Heapster] (https://github.com/kubernetes/heapster) as an additional storage backend.  

### Configuration

Coming soon...

### Details

v1: Pulls stats from InfluxDB on your Kubernetes cluster every 60s and sends to a RabbitMQ server you specify. Multiple clusters can send data to the same RabbitMQ server.
This centralized data can then be pulled from RabbitMQ and displayed on the present Kubernetes dashboard and future analytics dashboards.

### Coming soon:

v1.1: Configure the period in which the data is pulled.

v1.2: Option to pull existing stats already stored in InfluxDB to RabbitMQ. This will be done in the background as the stats data could be very large. 

### Comments

Contributions, questions, and comments are all welcomed and encouraged!

