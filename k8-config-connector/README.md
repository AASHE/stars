# Kubernetes Config Connector

Config Connector is a Kubernetes addon that allows you to manage Google Cloud resources through Kubernetes.  Overview of Config Connector is [here](https://cloud.google.com/config-connector/docs/overview)

## Namespace


## Installation
Config Connector was selected as install option in the GKE Cluster.  Config Connector provides a collection of Kubernetes Custom Resource Definitions and controllers to provision GCP resources.  The next setup step is create a service account, grant roles to that service account, and add in Workload Identity User permissions.  The [config-conn-setup.sh](config-conn-setup.sh) script in this directory is provided in case this needs to be performed again in the future.

## Validate Config Connector

To validate Config Connector is running correctly enter `kubectl wait -n cnrm-system --for=condition=Ready pod --all`
