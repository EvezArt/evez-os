#!/usr/bin/env bash
# =============================================================================
# GCP Service Account Setup for EVEZ Firmament
# Creates a service account, grants roles, downloads key, activates gcloud auth
# Usage: ./gcp-service-account.sh <PROJECT_ID> [REGION]
# =============================================================================
set -euo pipefail

PROJECT_ID="${1:-evez-firmament}"
REGION="${2:-us-central1}"
SA_NAME="evez-mesh-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="${HOME}/.config/gcloud/${SA_NAME}-key.json"
KEY_DIR="${HOME}/.config/gcloud"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERR]${NC} $*"; }

# ─── Pre-flight ──────────────────────────────────────────────────────────────
check_existing_auth() {
    info "Checking for existing GCP authentication..."

    # Check 1: Application Default Credentials
    if [[ -f "${HOME}/.config/gcloud/application_default_credentials.json" ]]; then
        ok "Application Default Credentials found"
        return 0
    fi

    # Check 2: GOOGLE_APPLICATION_CREDENTIALS env var
    if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]]; then
        ok "GOOGLE_APPLICATION_CREDENTIALS set: ${GOOGLE_APPLICATION_CREDENTIALS}"
        return 0
    fi

    # Check 3: gcloud auth list
    if gcloud auth list --format=json 2>/dev/null | jq -e '.[] | select(.status=="ACTIVE")' &>/dev/null; then
        ok "Active gcloud account found"
        return 0
    fi

    # Check 4: GCE metadata server
    if curl -sf -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/" &>/dev/null; then
        ok "GCE metadata server available (running on GCP)"
        return 0
    fi

    # Check 5: Any existing service account key
    for f in "${HOME}"/.config/gcloud/*-key.json; do
        if [[ -f "$f" ]]; then
            ok "Existing service account key found: $f"
            info "Activating..."
            gcloud auth activate-service-account --key-file="$f" --project="${PROJECT_ID}"
            export GOOGLE_APPLICATION_CREDENTIALS="$f"
            return 0
        fi
    done

    warn "No GCP authentication found. Starting guided setup..."
    return 1
}

# If we already have auth, we're done
if check_existing_auth; then
    ok "GCP authentication is already configured!"
    echo ""
    info "To verify: gcloud auth list"
    info "Project: $(gcloud config get-value project 2>/dev/null || echo 'not set')"

    # Ensure GOOGLE_APPLICATION_CREDENTIALS is in shell rc
    if [[ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]]; then
        for rcfile in .bashrc .zshrc .profile; do
            rcpath="${HOME}/${rcfile}"
            if [[ -f "${rcpath}" ]] && ! grep -q "GOOGLE_APPLICATION_CREDENTIALS" "${rcpath}"; then
                echo "export GOOGLE_APPLICATION_CREDENTIALS=\"${GOOGLE_APPLICATION_CREDENTIALS}\"" >> "${rcpath}"
                info "Added GOOGLE_APPLICATION_CREDENTIALS to ${rcfile}"
            fi
        done
    fi
    exit 0
fi

# ─── Interactive Console Setup ───────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "  EVEZ GCP Service Account Setup"
echo "  Project: ${PROJECT_ID}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "This script will guide you through creating a GCP service account."
echo "You need a GCP account with billing enabled."
echo ""

# Step 1: Check if gcloud is installed
if ! command -v gcloud &>/dev/null; then
    err "gcloud CLI not found. Installing..."
    curl https://sdk.cloud.google.com | bash
    exec bash "$0" "$@"
fi

ok "gcloud CLI found: $(gcloud version --format=json 2>/dev/null | jq -r '.Google Cloud SDK // "unknown"')"

# Step 2: Check if user wants to do it via console or CLI
echo ""
echo "Choose setup method:"
echo "  1) Automatic (uses gcloud CLI — requires browser login first)"
echo "  2) Manual Console (step-by-step guide with copy-paste)"
echo "  3) I already have a key file (provide path)"
echo ""
read -rp "Enter choice [1-3]: " method_choice

case "${method_choice}" in
    1)
        info "Starting browser-based login..."
        gcloud auth login --project="${PROJECT_ID}"
        ;;
    2)
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  MANUAL SETUP GUIDE"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Step 1: Open the GCP Console"
        echo "  → https://console.cloud.google.com/iam-admin/serviceaccounts?project=${PROJECT_ID}"
        echo ""
        echo "Step 2: Click '+ CREATE SERVICE ACCOUNT'"
        echo "  Name: ${SA_NAME}"
        echo "  Description: EVEZ Mesh service account for multi-node deployment"
        echo "  Click 'Create and Continue'"
        echo ""
        echo "Step 3: Add these roles:"
        echo "  ✓ Compute Admin"
        echo "  ✓ Kubernetes Engine Admin"
        echo "  ✓ Cloud SQL Admin"
        echo "  ✓ DNS Administrator"
        echo "  ✓ Monitoring Admin"
        echo "  ✓ Logging Admin"
        echo "  ✓ Security Admin"
        echo "  ✓ Service Account User"
        echo "  ✓ Storage Admin"
        echo "  ✓ IAM Security Admin"
        echo "  Click 'Continue'"
        echo ""
        echo "Step 4: Click 'Done' (skip granting user access)"
        echo ""
        echo "Step 5: Click the service account → 'Keys' tab → 'Add Key' → 'Create new key' → JSON → Download"
        echo ""
        echo "Step 6: Save the downloaded file to: ${KEY_FILE}"
        echo ""
        read -rp "Press Enter when you've downloaded the key to ${KEY_FILE}..."

        if [[ ! -f "${KEY_FILE}" ]]; then
            read -rp "Enter path to downloaded key file: " user_key_path
            if [[ -f "${user_key_path}" ]]; then
                mkdir -p "${KEY_DIR}"
                cp "${user_key_path}" "${KEY_FILE}"
                chmod 600 "${KEY_FILE}"
                ok "Key copied to ${KEY_FILE}"
            else
                err "File not found: ${user_key_path}"
                exit 1
            fi
        fi
        ;;
    3)
        read -rp "Enter path to existing key file: " user_key_path
        if [[ -f "${user_key_path}" ]]; then
            mkdir -p "${KEY_DIR}"
            cp "${user_key_path}" "${KEY_FILE}"
            chmod 600 "${KEY_FILE}"
            ok "Key copied to ${KEY_FILE}"
        else
            err "File not found: ${user_key_path}"
            exit 1
        fi
        ;;
    *)
        err "Invalid choice"
        exit 1
        ;;
esac

# ─── Activate Service Account ────────────────────────────────────────────────
if [[ -f "${KEY_FILE}" ]]; then
    info "Activating service account..."
    gcloud auth activate-service-account --key-file="${KEY_FILE}" --project="${PROJECT_ID}"
    ok "Service account activated!"

    # Set as default
    gcloud config set core/project "${PROJECT_ID}"
    gcloud config set compute/region "${REGION}"
    gcloud config set compute/zone "${REGION}-a"

    # Export env var
    export GOOGLE_APPLICATION_CREDENTIALS="${KEY_FILE}"

    # Add to shell rc files
    for rcfile in .bashrc .zshrc .profile; do
        rcpath="${HOME}/${rcfile}"
        if [[ -f "${rcpath}" ]]; then
            if ! grep -q "GOOGLE_APPLICATION_CREDENTIALS" "${rcpath}"; then
                {
                    echo ""
                    echo "# GCP Service Account for EVEZ"
                    echo "export GOOGLE_APPLICATION_CREDENTIALS=\"${KEY_FILE}\""
                } >> "${rcpath}"
                info "Added GOOGLE_APPLICATION_CREDENTIALS to ${rcfile}"
            fi
        fi
    done

    # Verify
    echo ""
    ok "════════════════════════════════════════════════"
    ok "  GCP Authentication Setup Complete!"
    ok "════════════════════════════════════════════════"
    echo ""
    info "Service Account: ${SA_EMAIL}"
    info "Project: ${PROJECT_ID}"
    info "Region: ${REGION}"
    info "Key file: ${KEY_FILE}"
    echo ""
    info "Test with: gcloud compute instances list"
    info "Bootstrap with: ./gcp-bootstrap.sh"
else
    err "Key file not found at ${KEY_FILE}. Setup incomplete."
    exit 1
fi
