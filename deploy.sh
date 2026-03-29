#!/bin/bash
# =============================================================================
# deploy.sh — Deploy Skill Investment Portfolio Engine to Google Cloud Run
# =============================================================================
# Prerequisites:
#   1. gcloud CLI installed: https://cloud.google.com/sdk/docs/install
#   2. Docker Desktop running
#   3. Run once: gcloud auth login && gcloud auth configure-docker us-central1-docker.pkg.dev
#
# Usage:
#   export BRIGHT_DATA_API_KEY=your_key
#   export FEATHERLESS_API_KEY=your_key
#   bash deploy.sh
# =============================================================================

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="us-central1"
REPO="skill-portfolio"                          # Artifact Registry repo name
BACKEND_SVC="skill-portfolio-backend"
FRONTEND_SVC="skill-portfolio-frontend"
BACKEND_IMG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend:latest"
FRONTEND_IMG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/frontend:latest"

if [ -z "$PROJECT_ID" ]; then
  echo "❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

echo "🚀 Deploying to GCP project: ${PROJECT_ID} | region: ${REGION}"

# ── 1. Enable required APIs ───────────────────────────────────────────────────
echo "⚙️  Enabling GCP APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  --project="${PROJECT_ID}" --quiet

# ── 2. Create Artifact Registry repo (idempotent) ─────────────────────────────
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create "${REPO}" \
  --repository-format=docker \
  --location="${REGION}" \
  --project="${PROJECT_ID}" \
  --quiet 2>/dev/null || echo "   (repo already exists, skipping)"

# ── 3. Build & push backend ───────────────────────────────────────────────────
echo "🔨 Building backend image..."
docker build -t "${BACKEND_IMG}" ./backend

echo "⬆️  Pushing backend image..."
docker push "${BACKEND_IMG}"

echo "☁️  Deploying backend to Cloud Run..."
gcloud run deploy "${BACKEND_SVC}" \
  --image="${BACKEND_IMG}" \
  --platform=managed \
  --region="${REGION}" \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --timeout=60 \
  --set-env-vars="BRIGHT_DATA_API_KEY=${BRIGHT_DATA_API_KEY:-},FEATHERLESS_API_KEY=${FEATHERLESS_API_KEY:-},GOOGLE_CLOUD_PROJECT=${PROJECT_ID},ENVIRONMENT=production" \
  --project="${PROJECT_ID}" \
  --quiet

BACKEND_URL=$(gcloud run services describe "${BACKEND_SVC}" \
  --platform=managed --region="${REGION}" \
  --format="value(status.url)" \
  --project="${PROJECT_ID}")

echo "✅ Backend live at: ${BACKEND_URL}"

# ── 4. Build & push frontend ──────────────────────────────────────────────────
echo "🔨 Building frontend image (API_URL=${BACKEND_URL})..."
docker build \
  --build-arg REACT_APP_API_URL="${BACKEND_URL}" \
  -t "${FRONTEND_IMG}" \
  ./frontend

echo "⬆️  Pushing frontend image..."
docker push "${FRONTEND_IMG}"

echo "☁️  Deploying frontend to Cloud Run..."
gcloud run deploy "${FRONTEND_SVC}" \
  --image="${FRONTEND_IMG}" \
  --platform=managed \
  --region="${REGION}" \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --project="${PROJECT_ID}" \
  --quiet

FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SVC}" \
  --platform=managed --region="${REGION}" \
  --format="value(status.url)" \
  --project="${PROJECT_ID}")

# ── 5. Done ───────────────────────────────────────────────────────────────────
echo ""
echo "🎉 Deployment complete!"
echo "   Frontend : ${FRONTEND_URL}"
echo "   Backend  : ${BACKEND_URL}"
echo "   API Docs : ${BACKEND_URL}/docs"
