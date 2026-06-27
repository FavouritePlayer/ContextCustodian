#!/usr/bin/env bash
# Activates the Actian VectorAI trial/product key against a running
# container via its REST API (the same call the Local UI's License Manager
# page makes at /dashboard/license — no docker env var involved).
#
# Get the product key from your Actian account (format:
# XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX) and put it in .env as
# ACTIAN_PRODUCT_KEY before running this.
set -euo pipefail

cd "$(dirname "$0")/.."
if [ -f .env ]; then
  set -a; source .env; set +a
fi

: "${ACTIAN_PRODUCT_KEY:?Set ACTIAN_PRODUCT_KEY in .env first}"
REST_HOST="${VECTORAI_REST_HOST:-localhost:6573}"

curl -s -X POST "http://${REST_HOST}/licenses/add" \
  -H "Content-Type: application/json" \
  -d "{\"product_key\":\"${ACTIAN_PRODUCT_KEY}\"}"
echo
echo "--- status ---"
curl -s "http://${REST_HOST}/licenses/status"
echo
