#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

if ! command -v python3 &> /dev/null; then
    echo "[!] python3 could not be found."
    echo "    Please install Python 3.8+ to use this script."
    exit 1
fi

python3 -m antigravity_restore.cli "$@"
