#!/bin/bash

# Stop if error occurs
set -e

# RABBIT_HOST is the mandatory argument
if [ "$#" == 0 ]; then
   # Set default RABBIT_HOST to Pete's RabbitMQ server
   export RABBIT_HOST=104.197.113.124
else
   # Configure supplied host
   export RABBIT_HOST=$1
fi

# File's location (with write access)
INFLUBBIT_DIR=$HOME/.influbbit
if [ ! -d $INFLUBBIT_DIR ]; then
    mkdir -p $INFLUBBIT_DIR
fi

# Discover location of InfluxDB
INFLUX_POD=$(kubectl get pod --namespace=kube-system | grep influx | cut -d " " -f 1)
export INFLUX_HOST=$(kubectl describe pod --namespace=kube-system $INFLUX_POD | grep "Node:" | tr -d [:blank:] | cut -d ":" -f 2 | cut -d "/" -f 2)
export INFLUX_NODE_NAME=$(kubectl describe pod --namespace=kube-system $INFLUX_POD | grep "Node:" | cut -d "/" -f 1 | tr -d [:blank:] | cut -d ":" -f 2)
export CLUSTER_IP=$(kubectl cluster-info | grep "master" | cut -d "/" -f 3 | cut -d ":" -f 1)

# Behavior of this script can be changed
# setting different environment variables
if [ "$NAMESPACE" == "" ]; then export NAMESPACE="default"; fi
if [ "$DEBUG_MODE" == "" ]; then export DEBUG_MODE="0"; fi
if [ "$IDLE_WAIT_SECS" == "" ]; then export IDLE_WAIT_SECS="10"; fi
if [ "$CLUSTER_NAME" == "" ]; then export CLUSTER_NAME="kubernetes"; fi

if [ "$INFLUX_HOST" == "" ]; then export INFLUX_HOST="localhost"; fi
if [ "$INFLUX_PORT" == "" ]; then export INFLUX_PORT="8086"; fi
if [ "$INFLUX_USER" == "" ]; then export INFLUX_USER="root"; fi
if [ "$INFLUX_PWD" == "" ]; then export INFLUX_PWD="root"; fi
if [ "$INFLUX_DB" == "" ]; then export INFLUX_DB="k8s"; fi
if [ "$INFLUX_BATCH" == "" ]; then export INFLUX_BATCH="100"; fi

if [ "$RABBIT_PORT" == "" ]; then export RABBIT_PORT="5672"; fi
if [ "$RABBIT_VHOST" == "" ]; then export RABBIT_VHOST="/"; fi
if [ "$RABBIT_USER" == "" ]; then export RABBIT_USER="guest"; fi
if [ "$RABBIT_PWD" == "" ]; then export RABBIT_PWD="guest"; fi
if [ "$RABBIT_QUEUE" == "" ]; then export RABBIT_QUEUE="test_q"; fi
if [ "$RABBIT_EXCHANGE" == "" ]; then export RABBIT_EXCHANGE="test_exchange"; fi
if [ "$RABBIT_BATCH" == "" ]; then export RABBIT_BATCH="100"; fi

# Configure context/namespace to run influbbit
export CONTEXT=$(kubectl config view | grep current-context | awk '{print $2}')
kubectl config set-context $CONTEXT --namespace=$NAMESPACE

# Download files
curl -s https://raw.githubusercontent.com/peteper2001/nflbtemp/master/k8s/controller.yml > $INFLUBBIT_DIR/controller.yml
curl -s https://raw.githubusercontent.com/peteper2001/nflbtemp/master/k8s/dockersecret.yml > $INFLUBBIT_DIR/dockersecret.yml

# Delete old copy of Influbbit controller
echo "Uninstalling any previous version of Influbbit..."
kubectl delete --ignore-not-found=true -f $INFLUBBIT_DIR/controller.yml

# Launch secret to provide Docker hub credentials
kubectl delete --ignore-not-found=true -f $INFLUBBIT_DIR/dockersecret.yml
kubectl create -f $INFLUBBIT_DIR/dockersecret.yml

# Replace variables in controller.yml
echo "Configuring Influbbit variables..."
CONTROLLER=$INFLUBBIT_DIR/controller-final.yml
cp $INFLUBBIT_DIR/controller.yml $CONTROLLER
VARIABLES=$(awk -F"{|}" '{print $2}' $CONTROLLER)
for VARIABLE_NAME in $VARIABLES; do
    VARIABLE_VALUE=`echo ${!VARIABLE_NAME}`
    sed -i "s#{$VARIABLE_NAME}#${VARIABLE_VALUE}#" $CONTROLLER
done

# Launch new version of controller
echo "Launching Influbbit..."
kubectl create -f $CONTROLLER
rm -rf $CONTROLLER
sleep 3

echo "SUCCESS: Influbbit was launched."
echo "Heapster data will be pushed to:"
echo "         RabbitMQ server: $RABBIT_HOST"
echo "         RabbitMQ queue: $RABBIT_QUEUE"
echo "         RabbitMQ exchange: $RABBIT_EXCHANGE"

exit 0
