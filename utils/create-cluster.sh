#!/bin/bash

# Creates Kubernetes Cluster using gcloud.  gcloud must be installed first with gcloud init already ran

# set variables
PROJECT='aashe-migration'
ZONE='us-east1-b'
CLUSTER_NAME='aashe-gke-1'
CLUSTER_VERSION='1.16.13-gke.404'
RELEASE_CHANNEL='stable'
MACHINE_TYPE='e2-medium'
DISK_TYPE='pd-standard'
DISK_SIZE='100'
NUM_NODES='3'


gcloud beta container clusters create \
  --project $PROJECT \
  --zone $ZONE \
  --no-enable-basic-auth \
  --cluster-version $CLUSTER_VERSION \
  --release-channel $RELEASE_CHANNEL \
  --machine-type $MACHINE_TYPE \
  --image-type "COS" \
  --disk-type DISK_TYPE \
  --disk-size DISK_SIZE \
  --metadata disable-legacy-endpoints=true \
  --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" \
  --num-nodes $NUM_NODES \
  --enable-stackdriver-kubernetes \
  --enable-ip-alias \
  --network "projects/aashe-migration/global/networks/default" \
  --subnetwork "projects/aashe-migration/regions/us-east1/subnetworks/default" \
  --enable-intra-node-visibility \
  --default-max-pods-per-node "110" \
  --no-enable-master-authorized-networks \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,ConfigConnector \
  --enable-autoupgrade\
  --enable-autorepair \
  --max-surge-upgrade 1 \
  --max-unavailable-upgrade 0 \
  --workload-pool $PROJECT_ID".svc.id.goog" \
  --enable-shielded-nodes \
  --security-group "gke-security-groups@aashe.org" \
  $CLUSTER_NAME

  # set maintenance window, COSD, Network Policy, Service Account, autoscaling