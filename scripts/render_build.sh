#!/usr/bin/env bash
# Render build command for the context-custodian web service.
# Mirrors scripts/install.sh — the scalekit + actian protobuf/grpc pin dance.
# See Context_Custodian_MVP_4hr_Build.md Appendix A / risks section.
set -euo pipefail

cd "$(dirname "$0")/.."

pip install -r requirements.txt
pip install --no-deps scalekit-sdk-python
pip install "deprecation>=2.1.0" "Faker~=25.8.0" "google>=3.0" "mcp>=1.23.0" \
  "protoc-gen-openapiv2>=0.0.1" "PyJWT>=2.12.0" "setuptools<81.0,>=78.1.1" requests
# Re-pin after mcp/scalekit deps (mcp upgrades starlette; scalekit can downgrade protobuf).
# Do NOT pin grpcio-status<1.67 here — that range requires protobuf<6, which breaks Actian.
pip install "protobuf>=6.31.1,<7.0.0" "starlette>=0.40.0,<0.42.0"

echo "== render build smoke test =="
python scripts/check_env.py
