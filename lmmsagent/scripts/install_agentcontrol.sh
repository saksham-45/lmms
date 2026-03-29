#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="${1:-$ROOT_DIR/build}"
TARGET_DIR="${2:-$HOME/.lmms/plugins}"
PLUGIN_PATH="$BUILD_DIR/plugins/libAgentControl.so"

if [[ ! -f "$PLUGIN_PATH" ]]; then
  echo "Missing plugin at $PLUGIN_PATH" >&2
  echo "Run lmmsagent/scripts/build_agentcontrol.sh first" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp "$PLUGIN_PATH" "$TARGET_DIR/libAgentControl.so"

echo "Installed AgentControl plugin to: $TARGET_DIR/libAgentControl.so"
