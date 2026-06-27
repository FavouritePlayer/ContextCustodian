#!/usr/bin/env bash
# scalekit-sdk-python and actian-vectorai-client both pin protobuf, and the
# ranges only overlap in a narrow band. Verified empirically against the
# versions on PyPI as of this build (scalekit-sdk-python 2.12.0 wants
# protobuf<7.0.0,>=5.29.5 and grpcio-status<1.67,>=1.64; actian-vectorai-client
# needs protobuf gencode>=6.31.1, which is newer than scalekit's own floor).
# The build doc's original pin direction (protobuf/grpcio-status UP to
# >=6.31.1/>=1.67.0) was for older package versions and is now backwards —
# this is the corrected pin. Install scalekit with --no-deps, then its other
# transitive deps, then re-pin protobuf/grpcio-status into the working band.
# This bites on Render too — run the same sequence there.
set -euo pipefail

cd "$(dirname "$0")/.."
pip install -r requirements.txt
pip install --no-deps scalekit-sdk-python
pip install "deprecation>=2.1.0" "Faker~=25.8.0" "google>=3.0" "mcp>=1.23.0" \
  "protoc-gen-openapiv2>=0.0.1" "PyJWT>=2.12.0" "setuptools<81.0,>=78.1.1" requests
pip install "protobuf>=6.31.1,<7.0.0" "grpcio-status>=1.64,<1.67"
