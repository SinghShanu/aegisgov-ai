#!/usr/bin/env bash
# ==============================================================================
# AegisGov AI: Safe Cloud Deployment Script
# Guarantees deployment only onto the secondary free-tier GCP account & project.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 1. Run strict account pre-flight verification
"${SCRIPT_DIR}/verify_gcp_account.sh"

# Load environment using robust parser
if [ -f "${ROOT_DIR}/.env" ]; then
    while IFS="=" read -r key value || [ -n "$key" ]; do
        key=$(echo "${key}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        value=$(echo "${value}" | sed -e 's/^[[:space:]]*["'"'"']//' -e 's/["'"'"'][[:space:]]*$//')
        export "${key}=${value}"
    done < "${ROOT_DIR}/.env"
fi

TARGET_ACCOUNT="${GCP_DEPLOY_ACCOUNT:-}"
TARGET_PROJECT="${GCP_PROJECT_ID:-aegisgov-ai-2026}"
REGION="${GCP_LOCATION:-asia-southeast1}"
REPO_NAME="aegisgov-repo"
IMAGE_TAG="${REGION}-docker.pkg.dev/${TARGET_PROJECT}/${REPO_NAME}/aegisgov-app:latest"
SERVICE_NAME="aegisgov-ai"

if [ -z "$TARGET_ACCOUNT" ]; then
    echo "❌ Missing GCP_DEPLOY_ACCOUNT in .env. Halting."
    exit 1
fi

echo ""
echo "======================================================"
echo " 🚀 AegisGov AI: Cloud Run Free-Tier Deployment Plan"
echo "======================================================"
echo "   Account  : ${TARGET_ACCOUNT}"
echo "   Project  : ${TARGET_PROJECT}"
echo "   Region   : ${REGION} (Singapore)"
echo "   Repo     : ${REPO_NAME}"
echo "   Image    : ${IMAGE_TAG}"
echo "   Service  : ${SERVICE_NAME}"
echo "   Limits   : max-instances=2, 512Mi RAM, 1 vCPU"
echo "======================================================"
echo ""

if [[ "${1:-}" =~ ^(-y|--yes)$ ]]; then
    confirm="y"
else
    read -rp "Proceed with build & deployment to ${TARGET_PROJECT} using ${TARGET_ACCOUNT}? (y/N) " confirm
fi
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled by user."
    exit 0
fi

echo ""
echo "🔧 Step 1: Ensuring required GCP services are enabled..."
gcloud services enable \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    --account="${TARGET_ACCOUNT}" \
    --project="${TARGET_PROJECT}"

echo ""
echo "📦 Step 2: Verifying Artifact Registry repository (${REPO_NAME})..."
if ! gcloud artifacts repositories describe "${REPO_NAME}" \
    --location="${REGION}" \
    --project="${TARGET_PROJECT}" \
    --account="${TARGET_ACCOUNT}" &>/dev/null; then
    echo "Creating Docker repository '${REPO_NAME}' in ${REGION}..."
    gcloud artifacts repositories create "${REPO_NAME}" \
        --repository-format=docker \
        --location="${REGION}" \
        --description="AegisGov AI Production Docker Repository" \
        --project="${TARGET_PROJECT}" \
        --account="${TARGET_ACCOUNT}"
else
    echo "Artifact Registry repository '${REPO_NAME}' is ready."
fi

echo ""
echo "🏗️ Step 3: Building container image via Google Cloud Build..."
gcloud builds submit "${ROOT_DIR}" \
    --account="${TARGET_ACCOUNT}" \
    --project="${TARGET_PROJECT}" \
    --tag="${IMAGE_TAG}"

echo ""
echo "🌟 Step 4: Deploying to Google Cloud Run with Free-Tier Guardrails..."
ENV_VARS="BASE_CURRENCY=SGD,ENVIRONMENT=production,GCP_MODE=local,GCP_PROJECT_ID=${TARGET_PROJECT}"
if [ -n "${GEMINI_API_KEY:-}" ]; then
    ENV_VARS="${ENV_VARS},GEMINI_API_KEY=${GEMINI_API_KEY}"
    echo "   Gemini API Key: Configured (Forwarding to Cloud Run)"
else
    echo "   Gemini API Key: None (Using Deterministic Governance Engine)"
fi

gcloud run deploy "${SERVICE_NAME}" \
    --account="${TARGET_ACCOUNT}" \
    --project="${TARGET_PROJECT}" \
    --image="${IMAGE_TAG}" \
    --region="${REGION}" \
    --platform="managed" \
    --allow-unauthenticated \
    --max-instances=2 \
    --memory=512Mi \
    --cpu=1 \
    --set-env-vars="${ENV_VARS}"

echo ""
echo "======================================================"
echo " ✅ DEPLOYMENT COMPLETE!"
echo "======================================================"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --account="${TARGET_ACCOUNT}" \
    --project="${TARGET_PROJECT}" \
    --region="${REGION}" \
    --format="value(status.url)")

echo "🌐 Live Application URL: ${SERVICE_URL}"
echo "🏥 Health Endpoint     : ${SERVICE_URL}/api/health"
echo "======================================================"
