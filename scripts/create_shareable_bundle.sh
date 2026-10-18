#!/usr/bin/env bash
# ==============================================================================
# AegisGov AI: Create Clean Shareable Project Bundle
# Packages code, docs, templates, and pre-built frontend into a lightweight zip
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_ZIP="${ROOT_DIR}/aegisgov-ai-shareable-bundle.zip"

echo "🔨 Ensuring frontend production bundle is fresh..."
if command -v npm &>/dev/null; then
    (cd "${ROOT_DIR}/frontend" && npm run build)
fi

echo "📦 Creating clean, lightweight project zip for teammate..."
rm -f "${OUTPUT_ZIP}"

cd "${ROOT_DIR}"
zip -r "${OUTPUT_ZIP}" . \
    -x "backend/venv/*" \
    -x "backend/venv/**" \
    -x "frontend/node_modules/*" \
    -x "frontend/node_modules/**" \
    -x ".env" \
    -x ".git/*" \
    -x ".git/**" \
    -x ".pytest_cache/*" \
    -x ".pytest_cache/**" \
    -x "**/__pycache__/*" \
    -x "**/__pycache__/**" \
    -x "*.pyc" \
    -x ".DS_Store" \
    -x "*/.DS_Store" \
    -x "aegisgov-ai-shareable-bundle.zip" \
    -x "*.eml" \
    -x "*.pdf" \
    -x "*.bak" \
    -x "*.pptx" \
    -x "*.odp"

echo ""
echo "✅ Shareable bundle created successfully!"
echo "📍 Location : ${OUTPUT_ZIP}"
echo "📊 Size     : $(du -h "${OUTPUT_ZIP}" | cut -f1)"
echo "💡 Share this zip file via Google Drive, AirDrop, or Slack."
