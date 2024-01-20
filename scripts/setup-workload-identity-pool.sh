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

gcloud iam workload-identity-pools create "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools describe "github" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)"

gcloud iam workload-identity-pools providers create-oidc "${REPO}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="My GitHub repo Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

WORKLOAD_IDENTITY_POOL_ID=gcloud iam workload-identity-pools providers describe "${REPO}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="github" \
  --format="value(name)"

echo "Workload identity provider ${WORKLOAWORKLOAD_IDENTITY_POOL_IDD_ID_PROVIDER} created for project ${PROJECT_ID}."

echo "Granting the ID provider access to GCP services..."

