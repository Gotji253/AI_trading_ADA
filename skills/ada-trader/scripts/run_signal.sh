#!/usr/bin/env bash
# Helper script for Hermes skill
cd "$(dirname "$0")/../.." || exit 1
python -m src.cli ada-signal "$@"
