#!/usr/bin/env bash
# Freeze the erh_core sidecar into a single-file binary with PyInstaller.
# Output: desktop/sidecar/dist/erh_sidecar[.exe]  (consumed by electron-builder
# extraResources). Safe to skip on platforms without Python — the app falls
# back to the Tier A JS scorer.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
cd "$HERE"

PY="${ERH_PYTHON:-python3}"

echo "[sidecar] using interpreter: $PY"
"$PY" -m pip install --upgrade pip >/dev/null
"$PY" -m pip install "pyinstaller>=6.0" numpy >/dev/null
# Make erh_core importable for the freeze.
"$PY" -m pip install -e "$REPO_ROOT" >/dev/null 2>&1 || \
  echo "[sidecar] editable install skipped (using PYTHONPATH=$REPO_ROOT)"

export PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}"

"$PY" -m PyInstaller \
  --onefile \
  --name erh_sidecar \
  --collect-submodules erh_core \
  --hidden-import numpy \
  --distpath dist \
  --workpath build \
  --specpath build \
  erh_sidecar.py

echo "[sidecar] built: $HERE/dist/"
ls -la dist || true
