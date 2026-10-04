#!/usr/bin/env bash
# ==============================================================================
# AegisGov AI: GCP Account & Billing Pre-Flight Safety Verifier
# Prevents accidental deployments to non-free-tier personal accounts.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}======================================================${NC}"
echo -e "${BLUE}${BOLD} 🛡️ AegisGov AI: GCP Account Safety & Free-Tier Guard  ${NC}"
echo -e "${BLUE}${BOLD}======================================================${NC}"

# Load .env if present
if [ -f "${ROOT_DIR}/.env" ]; then
    while IFS="=" read -r key value || [ -n "$key" ]; do
        key=$(echo "${key}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        value=$(echo "${value}" | sed -e 's/^[[:space:]]*["'"'"']//' -e 's/["'"'"'][[:space:]]*$//')
        export "${key}=${value}"
    done < "${ROOT_DIR}/.env"
fi

EXPECTED_ACCOUNT="${GCP_DEPLOY_ACCOUNT:-}"
EXPECTED_PROJECT="${GCP_PROJECT_ID:-aegisgov-ai-2026}"

if [ -z "$EXPECTED_ACCOUNT" ]; then
    echo -e "${RED}${BOLD}❌ ERROR: 'GCP_DEPLOY_ACCOUNT' is not set in your .env file.${NC}"
    echo -e "${YELLOW}To protect against accidental charges, you must explicitly configure your secondary free-tier email in .env:${NC}"
    echo -e "  ${BOLD}GCP_DEPLOY_ACCOUNT=\"your-secondary-email@gmail.com\"${NC}"
    echo ""
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ ERROR: 'gcloud' CLI is not found in PATH.${NC}"
    echo "Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Retrieve active gcloud account and project
ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "")
ACTIVE_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
ACTIVE_CONFIG=$(gcloud config configurations list --filter="IS_ACTIVE=true" --format="value(name)" 2>/dev/null || echo "default")

echo -e "Current gcloud Configuration : ${BOLD}${ACTIVE_CONFIG}${NC}"
echo -e "Currently Active Account     : ${BOLD}${ACTIVE_ACCOUNT:-[NONE]}${NC}"
echo -e "Currently Active Project     : ${BOLD}${ACTIVE_PROJECT:-[NONE]}${NC}"
echo -e "Configured Free-Tier Account : ${BOLD}${EXPECTED_ACCOUNT:-[NOT CONFIGURED]}${NC}"
echo -e "Configured Target Project    : ${BOLD}${EXPECTED_PROJECT}${NC}"
echo "------------------------------------------------------"

# Verification logic
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo -e "${RED}❌ NO ACTIVE GCLOUD ACCOUNT FOUND.${NC}"
    echo "Please run: gcloud auth login ${EXPECTED_ACCOUNT}"
    exit 1
fi

if [ -n "$EXPECTED_ACCOUNT" ] && [ "$ACTIVE_ACCOUNT" != "$EXPECTED_ACCOUNT" ]; then
    echo -e "${RED}${BOLD}🚨 CRITICAL SAFETY ALERT: ACCOUNT MISMATCH DETECTED!${NC}"
    echo -e "${RED}Your currently active gcloud account is: ${BOLD}${ACTIVE_ACCOUNT}${NC}"
    echo -e "${RED}Your intended free-tier account is    : ${BOLD}${EXPECTED_ACCOUNT}${NC}"
    echo ""
    echo -e "${YELLOW}🛑 DEPLOYMENT BLOCKED TO PREVENT CHARGES ON YOUR MAIN ACCOUNT.${NC}"
    echo ""
    echo -e "To switch to your free-tier account, run:"
    echo -e "  ${BOLD}gcloud config set account ${EXPECTED_ACCOUNT}${NC}"
    echo -e "Or create an isolated configuration for this project:"
    echo -e "  ${BOLD}gcloud config configurations activate aegisgov-freetier${NC}"
    exit 1
fi

if [ -n "$EXPECTED_PROJECT" ] && [ "$ACTIVE_PROJECT" != "$EXPECTED_PROJECT" ]; then
    echo -e "${YELLOW}⚠️ Notice: Active project (${ACTIVE_PROJECT}) differs from target (${EXPECTED_PROJECT}).${NC}"
    echo -e "Run: ${BOLD}gcloud config set project ${EXPECTED_PROJECT}${NC}"
fi

echo -e "${GREEN}${BOLD}✅ VERIFICATION PASSED!${NC}"
echo -e "${GREEN}Active account matches designated free-tier account: ${ACTIVE_ACCOUNT}${NC}"
echo -e "${GREEN}Safe to proceed with deployment.${NC}"
