#!/bin/sh

# Creates Kubernetes Cluster using gcloud.  gcloud must be installed first with gcloud init already ran

set -e

# set variables
PROJECT_ID='aashe-migration'
ZONE='us-east1-b'
CLUSTER_NAME='aashe-gke-2'
CLUSTER_VERSION='1.16.13-gke.404'
RELEASE_CHANNEL='stable'
MACHINE_TYPE='e2-medium'
DISK_TYPE='pd-standard'
DISK_SIZE='200GB'
NUM_NODES='3'


gcloud beta container clusters create $CLUSTER_NAME \
  --project $PROJECT_ID \
  --zone $ZONE \
  --no-enable-basic-auth \
  --cluster-version $CLUSTER_VERSION \
  --release-channel $RELEASE_CHANNEL \
  --machine-type $MACHINE_TYPE \
  --image-type "cos_containerd" \
  --disk-type $DISK_TYPE \
  --disk-size $DISK_SIZE \
  --metadata disable-legacy-endpoints=true \
  --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" \
  --num-nodes $NUM_NODES \
  --enable-stackdriver-kubernetes \
  --enable-ip-alias \
  --network "projects/aashe-migration/global/networks/default" \
  --subnetwork "projects/aashe-migration/regions/us-east1/subnetworks/default" \
  --enable-network-policy \
  --enable-intra-node-visibility \
  --default-max-pods-per-node "110" \
  --no-enable-master-authorized-networks \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,ConfigConnector \
  --enable-autoupgrade\
  --enable-autorepair \
  --max-surge-upgrade 1 \
  --max-unavailable-upgrade 0 \
  --maintenance-window-start "2020-12-06T06:00:00Z" \
  --maintenance-window-end "2020-12-07T06:00:00Z" \
  --maintenance-window-recurrence "FREQ=WEEKLY;BYDAY=SA,SU" \
  --workload-pool "${PROJECT_ID}.svc.id.goog" \
  --enable-shielded-nodes \
  --security-group "gke-security-groups@aashe.org"

  # set Service Account, autoscaling

echo "GKE Cluster provisioning complete at $(date)"
exit 0