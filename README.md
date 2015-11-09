# Influbbit Service

Influbbit is a Python service to pull data from the InfluxDB database used by Heapster (on a Kubernetes cluster)
and send that information to a remote RabbitMQ server outside of Kubernetes

## Code Organization

* The DEVELOP.md file is mostly a summary of notes used during the development. Can be used to create the development environment and install the required dependencies, learn how test the servers locally, how import an external InfluxDB database (from a production Kubernetes cluster) to make local tests, how create and upload the Docker image, etc.

* The Dockerfile is the file which describes how create the Influbbit Docker image which will be executed on Kubernetes. This image is based on Ubuntu 14.04 and installs the Python dependencies, imports the Python source code of Influbbit and set defaults for environment variables. Finally, it starts the Influbbit service using run.sh file.

* Below the "src" directory you will find the Python code.

  * The entrypoint is influbbit.py, which basically creates the objects for the different classes to use and check for new metrics regularly. This file is just the Influbbit "controller".
  * All the Influbbit logic is contained on files located on the "src/services" directory: 
    * A class for Sqlite (which handle all the persistence works)
    * A class for InfluxDB (which reads the metrics)
    * A class for RabbitMQ (which create the batchs and dispatch the information to RabbitMQ).

  * The "k8s" directory is the directory where the Kubernetes files are stored.
    * The "dockersecret.yml" contains the credentials to authenticate against Docker Hub and then pull the Influbbit Docker image there. 
    * The "controller.yml" file describes to Kubernetes how create a replication controller for Influbbit, how use dockersecret to pull the image, where mount the directory to store the sqlite database and the variables to be parameterized. Actually, controller.yml is just a "template" (read below)
    * The "influbbit-launcher.sh" file is the launcher of the Influbbit service. This is a bash script which detects the location of the InfluxDB container and -if some variables/configurations were not previously configured- assigns default values. This script remove any old copy of Influbbit and then creates a copy of controller.yml (our template) and replace the different variables with the real value currently on memory. Kubernetes will inject these variables to our container, and the Influbbit Pyhon program will read these variables from the o.s. environment. That's how the Influbbit service can be configured dynamically.
