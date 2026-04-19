#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${1:-$ROOT_DIR/dist/pdf_text_snapshots}"

export CLANG_MODULE_CACHE_PATH="${CLANG_MODULE_CACHE_PATH:-/tmp/clang-module-cache}"
mkdir -p "$CLANG_MODULE_CACHE_PATH"

swift "$ROOT_DIR/scripts/export_pdf_text_snapshots.swift" \
  --project-root "$ROOT_DIR" \
  --output-dir "$OUTPUT_DIR"
