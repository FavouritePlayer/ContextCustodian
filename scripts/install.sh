#!/usr/bin/env bash
# scalekit-sdk-python pins protobuf<7.0.0, which silently breaks
# actian-vectorai-client (writes fail with no error at insert time).
# Install scalekit with --no-deps, then re-pin protobuf/grpcio-status up.
# This bites on Render too — run the same sequence there.
set -euo pipefail

cd "$(dirname "$0")/.."
pip install -r requirements.txt
pip install --no-deps scalekit-sdk-python
pip install "protobuf>=6.31.1" "grpcio-status>=1.67.0"
