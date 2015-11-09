##########################################################
#
#               Dockerfile for Influbbit 
#
##########################################################

FROM ubuntu:14.04
MAINTAINER PetePerlegos (peteperl)
ENV REFRESHED_AT 2015-11-09

# Volume for sqlite file
VOLUME  ["/var/lib/influbbit"]

# Update packages
RUN apt-get -qqy update

# Install packages
RUN apt-get -y install python
RUN apt-get -y install python-pip
RUN apt-get -y install sqlite

# Install Python dependencies
RUN pip install python-daemon
RUN pip install pika
RUN pip install influxdb

# Create directories
RUN mkdir /var/run/influbbit
RUN mkdir /var/log/influbbit
RUN mkdir -p /opt/influbbit/services

# Copy source code
ENV CODE_REFRESHED_AT 2015-10-16
ADD src/influbbit.py /opt/influbbit/
ADD src/services/ /opt/influbbit/services/
RUN chmod +x /opt/influbbit/influbbit.py

# Install run.sh
ADD run.sh /usr/sbin/run.sh
RUN chmod +x /usr/sbin/run.sh

# Influbbit Default Variables
ENV IDLE_WAIT_SECS 10
ENV DEBUG_MODE 0
ENV CLUSTER_NAME kubernetes
ENV CLUSTER_IP 127.0.0.1

# InfluxDB Default Variables
ENV INFLUX_HOST localhost
ENV INFLUX_PORT 8086
ENV INFLUX_USER root
ENV INFLUX_PWD root
ENV INFLUX_DB k8s
ENV INFLUX_BATCH 100

# RabbitMQ Default Variables
ENV RABBIT_HOST localhost
ENV RABBIT_PORT 5672
ENV RABBIT_VHOST /
ENV RABBIT_USER guest
ENV RABBIT_PWD guest
ENV RABBIT_QUEUE test_q
ENV RABBIT_EXCHANGE test_exchange
ENV RABBIT_BATCH 100

# Start service
ENTRYPOINT ["/usr/sbin/run.sh"]
