#!/usr/bin/env bash
# Deploy space-launches to Cloud Run
set -euo pipefail

PROJECT_ID="space-launches-app"
REGION="us-central1"
REPO="space-launches-repo"
IMAGE_NAME="space-launches"
SERVICE_NAME="space-launches"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:latest"

echo "==> Deploying to Cloud Run"

# Setup
echo "==> Setting up GCP project"
gcloud config set project "${PROJECT_ID}"
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com

# Create repo if needed
if ! gcloud artifacts repositories describe "${REPO}" --location="${REGION}" >/dev/null 2>&1; then
  echo "==> Creating Artifact Registry repository"
  gcloud artifacts repositories create "${REPO}" \
    --repository-format=docker \
    --location="${REGION}"
fi

# Build
echo "==> Building image with Cloud Build"
gcloud builds submit \
  --config=cloudbuild.yaml \
  --timeout=1800s

echo "==> Build complete"

# Verify required secrets exist before deploying, so a missing secret fails
# fast here instead of crashing the container after deploy.
for secret in SECRET_KEY ADMIN_PASSWORD_HASH; do
  if ! gcloud secrets describe "${secret}" >/dev/null 2>&1; then
    echo "ERROR: Secret '${secret}' does not exist. Create it first, e.g.:"
    echo "  printf '%s' 'your-value' | gcloud secrets create ${secret} --data-file=-"
    exit 1
  fi
done

# Deploy
echo "==> Deploying to Cloud Run"
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_URI}" \
  --region="${REGION}" \
  --port=5000 \
  --allow-unauthenticated \
  --memory=1Gi \
  --timeout=300 \
  --set-env-vars="ADMIN_USERNAME=admin" \
  --set-secrets="SECRET_KEY=SECRET_KEY:latest,ADMIN_PASSWORD_HASH=ADMIN_PASSWORD_HASH:latest"

echo "==> ✓ Deployment complete!"
echo ""
echo "==> Service URL:"
gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --format="value(status.url)"