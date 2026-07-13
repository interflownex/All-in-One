#!/usr/bin/env bash
set -euo pipefail
PROJECT="all-in-one-498012"

echo "Configuring project: $PROJECT"
gcloud config set project "$PROJECT"

echo "Enabling required APIs: Cloud Build, Container, Artifact Registry, Apigee, IAM"
gcloud services enable \
  cloudbuild.googleapis.com \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  apigee.googleapis.com \
  iam.googleapis.com \
  --project="$PROJECT"

echo "Installing gcloud components (kubectl, skaffold) if missing"
if ! command -v kubectl >/dev/null 2>&1; then
  gcloud components install kubectl --quiet || true
fi
if ! command -v skaffold >/dev/null 2>&1; then
  gcloud components install skaffold --quiet || true
fi

echo "Cloud Build and Cloud Code prerequisites configured. Next steps:"
echo "  1) Run: gcloud auth login"
echo "  2) Run: gcloud auth application-default login"
echo "  3) In VS Code, open Command Palette and run: Cloud Code: Set GCP Project"

echo "Done."
