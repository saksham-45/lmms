#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="${1:-$ROOT_DIR/build}"
JOBS="$(sysctl -n hw.ncpu 2>/dev/null || echo 4)"

cmake -S "$ROOT_DIR" -B "$BUILD_DIR"
cmake --build "$BUILD_DIR" --target AgentControl -j"$JOBS"

echo "Built AgentControl plugin at: $BUILD_DIR/plugins/libAgentControl.so"
