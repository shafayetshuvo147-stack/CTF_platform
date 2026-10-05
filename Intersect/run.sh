#!/usr/bin/env bash
# Bash Single Command Launcher for CTF Platform
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting CTF Platform..."
python3 start.py
