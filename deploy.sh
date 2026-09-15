#!/usr/bin/env bash
# Build, push, and deploy space-launches to Cloud Run via Artifact Registry (podman).
set -euo pipefail

# ---- Config ----
PROJECT_ID="space-launches-app"
REGION="us-central1"
REPO="space-launches-repo"
IMAGE_NAME="space-launches"
SERVICE_NAME="space-launches"
SERVICE_ACCOUNT="space-launches-sa@${PROJECT_ID}.iam.gserviceaccount.com"
PORT="5000"

# Tag with today's date, e.g. 9-14-2026 (no leading zeros, matches your convention)
TAG="$(date +%-m-%-d-%Y)"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}:${TAG}"

echo "==> Deploying ${IMAGE_URI}"

# ---- One-time setup (safe to re-run; commands are idempotent/no-ops if already done) ----
echo "==> Setting project"
gcloud config set project "${PROJECT_ID}" >/dev/null

echo "==> Ensuring required APIs are enabled"
gcloud services enable artifactregistry.googleapis.com run.googleapis.com iam.googleapis.com

echo "==> Ensuring Artifact Registry repo exists"
if ! gcloud artifacts repositories describe "${REPO}" --location="${REGION}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="space-launches images"
fi

echo "==> Ensuring runtime service account exists"
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${IMAGE_NAME}-sa" \
    --display-name="space-launches runtime"
fi

# ---- Auth podman to Artifact Registry ----
echo "==> Authenticating podman to Artifact Registry"
gcloud auth print-access-token | podman login -u oauth2accesstoken --password-stdin "https://${REGION}-docker.pkg.dev"

# ---- Build ----
echo "==> Building image"
podman build --platform=linux/amd64 -t "${IMAGE_URI}" .

# ---- Push ----
echo "==> Pushing image"
podman push "${IMAGE_URI}"

# ---- Deploy ----
echo "==> Deploying to Cloud Run"
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE_URI}" \
  --region="${REGION}" \
  --service-account="${SERVICE_ACCOUNT}" \
  --port="${PORT}" \
  --allow-unauthenticated

echo "==> Done. Service URL:"
gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --format="value(status.url)"