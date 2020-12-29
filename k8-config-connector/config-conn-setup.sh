#!/bin/sh

PROJECT_ID=aashe-migration
SERVICE_ACCOUNT_NAME=gke-config-conn

gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --description="Service Account for GKE Config Connector" \
    --display-name="GKE Config Conector"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/owner"

gcloud iam service-accounts add-iam-policy-binding \
${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
    --member="serviceAccount:${PROJECT_ID}.svc.id.goog[cnrm-system/cnrm-controller-manager]" \
    --role="roles/iam.workloadIdentityUser"