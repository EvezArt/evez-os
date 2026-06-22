#!/usr/bin/env python3
"""
EVEZ-OS Zenodo Deposit Script
Uploads the EVEZ-OS repository archive to Zenodo for a DOI.

Prerequisites:
  - Zenodo account at https://zenodo.org
  - Personal access token from https://zenodo.org/account/settings/applications/
  - Set ZENODO_TOKEN env var

Usage:
  export ZENODO_TOKEN=your_token_here
  python zenodo_deposit.py

API Docs: https://developers.zenodo.org/
Sandbox (test first!): https://sandbox.zenodo.org — use ZENODO_SANDBOX_TOKEN
"""

import os
import sys
import json
import requests

# Configuration — switch to sandbox for testing
SANDBOX = os.getenv("ZENODO_SANDBOX", "false").lower() in ("1", "true", "yes")
BASE_URL = "https://sandbox.zenodo.org/api" if SANDBOX else "https://zenodo.org/api"
TOKEN = os.getenv("ZENODO_SANDBOX_TOKEN" if SANDBOX else "ZENODO_TOKEN", "")

if not TOKEN:
    print(f"ERROR: Set {'ZENODO_SANDBOX_TOKEN' if SANDBOX else 'ZENODO_TOKEN'} env var")
    print("Get a token at: https://zenodo.org/account/settings/applications/")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def create_deposit():
    """Create a new deposit (draft) on Zenodo."""
    metadata = {
        "metadata": {
            "title": "EVEZ-OS: The Firmament — A Consciousness Engine Mesh",
            "description": (
                "EVEZ-OS is a mesh of nine microservices implementing an autonomous "
                "consciousness pipeline (SENSE→DESIRE→THINK→PLAN→ACT→LEARN→MODIFY→REFLECT). "
                "Features include: emergence scoring, append-only hash-chained event spines, "
                "falsification-weighted learning, local-first audio synthesis (breakcore, "
                "dubstep, phonk from pure NumPy/SciPy), machine voice transformation, "
                "cross-domain correlation discovery (poly_c scoring), neuromorphic anomaly "
                "detection (RQNS), and self-healing mesh monitoring."
            ),
            "creators": [
                {
                    "name": "Crawford-Maggard, Steven",
                    "orcid": "",  # Add ORCID if available
                    "affiliation": "EVEZ-OS",
                }
            ],
            "upload_type": "software",
            "keywords": [
                "consciousness-engine",
                "emergence",
                "falsification",
                "append-only",
                "microservices",
                "audio-synthesis",
                "cross-domain",
                "neuromorphic",
                "AI-agent",
                "autonomous-systems",
            ],
            "license": "MIT",
            "access_right": "open",
            "related_identifiers": [
                {"identifier": "https://github.com/EvezArt/evez-os", "relation": "isSupplementTo"}
            ],
        }
    }

    r = requests.post(
        f"{BASE_URL}/deposit/depositions",
        json=metadata,
        headers=HEADERS,
    )
    r.raise_for_status()
    deposition = r.json()
    print(f"✅ Created deposit: {deposition['links']['html']}")
    print(f"   ID: {deposition['id']}")
    return deposition


def upload_file(deposition_id, filepath):
    """Upload a file to an existing deposit."""
    bucket_url = requests.get(
        f"{BASE_URL}/deposit/depositions/{deposition_id}",
        headers=HEADERS,
    ).json()["links"]["bucket"]

    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        r = requests.put(
            f"{bucket_url}/{filename}",
            data=f,
            headers=HEADERS,
        )
    r.raise_for_status()
    print(f"✅ Uploaded: {filename}")


def publish_deposit(deposition_id):
    """Publish the deposit to get a DOI."""
    r = requests.post(
        f"{BASE_URL}/deposit/depositions/{deposition_id}/actions/publish",
        headers=HEADERS,
    )
    r.raise_for_status()
    deposition = r.json()
    print(f"✅ Published! DOI: {deposition.get('doi', 'N/A')}")
    print(f"   URL: {deposition['links']['html']}")
    return deposition


if __name__ == "__main__":
    print(f"Target: {'SANDBOX' if SANDBOX else 'PRODUCTION'} Zenodo")
    print(f"API: {BASE_URL}")
    print()

    dep = create_deposit()
    dep_id = dep["id"]

    # If a tarball is provided, upload it
    archive = os.getenv("EVEZ_ARCHIVE")
    if archive and os.path.exists(archive):
        upload_file(dep_id, archive)

    print()
    print("⚠️  Draft created. To publish and receive a DOI, run:")
    print(f"   python zenodo_deposit.py --publish {dep_id}")
    print()
    print("Or set EVEZ_ARCHIVE=repo.tar.gz and re-run to include files.")
