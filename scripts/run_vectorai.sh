#!/usr/bin/env bash
# Runs Actian VectorAI locally in Docker (build doc Appendix A).
# Requires Docker Desktop running first.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p local_data

docker run -d --name vectorai \
  -v "$(pwd)/local_data:/var/lib/actian-vectorai" \
  -p 6573-6575:6573-6575 \
  -e ACTIAN_VECTORAI_ACCEPT_EULA=YES \
  actian/vectorai:latest

echo "VectorAI starting on localhost:6574 — tail logs with: docker logs -f vectorai"
