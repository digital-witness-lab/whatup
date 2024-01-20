#!/bin/bash

set -e

if [ -z "${PROJECT_ID:-}" ]; then
    echo "Please set PROJECT_ID and re-run."
    exit 1
fi

REPO_OWNER="digital-witness-lab"
REPO_NAME="whatup"
REPO_SLUG="${REPO_OWNER}/${REPO_NAME}"

echo "****************************"
echo "This script only works when executed by a user who has admin-level privileges in the project ${PROJECT_ID}."
echo "****************************"

read -p "Press Enter to continue or Ctrl+c to quit..."

SERVICE_ACCOUNT_NAME="github-actions-service-account"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
  --project "${PROJECT_ID}"

gcloud iam workload-identity-pools create "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --description="Workload identity pool used for running Pulumi in GitHub Actions"

gcloud iam workload-identity-pools describe "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)"

gcloud iam workload-identity-pools providers create-oidc "${REPO_NAME}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="GitHub repo Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

WORKLOAD_IDENTITY_POOL_ID=gcloud iam workload-identity-pools providers describe "${REPO_NAME}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github" \
  --format="value(name)" 

echo "****************************"
echo "Granting the workload ID pool access to GCP services..."
echo "****************************"

# First, allow authentications from the Workload Identity Pool to the service account.
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${REPO_SLUG}"

function grant_role_to_service_account() {
  role=$1

  gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_EMAIL}" \
    --project="${PROJECT_ID}" \
    --role="${role}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}"
}

grant_role_to_service_account "roles/artifactregistry.admin"
grant_role_to_service_account "roles/bigquery.admin"
grant_role_to_service_account "roles/cloudkms.admin"
grant_role_to_service_account "roles/cloudsql.admin"
grant_role_to_service_account "roles/compute.networkAdmin" # For VPC, firewall and other networking resources.
grant_role_to_service_account "roles/iam.serviceAccountAdmin"
grant_role_to_service_account "roles/run.admin" # Cloud Run.
grant_role_to_service_account "roles/secretmanager.admin"
grant_role_to_service_account "roles/storage.admin"

echo "****************************"
echo "Workload identity pool ${WORKLOAD_IDENTITY_POOL_ID} created for project ${PROJECT_ID}."
echo "The workload identity pool has been granted access to the service account ${SERVICE_ACCOUNT_EMAIL}"
echo "****************************"
