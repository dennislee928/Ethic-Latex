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
# numpy/scipy/networkx are erh_core runtime deps; install them explicitly so
# the freeze still works when the editable install below is skipped.
"$PY" -m pip install "pyinstaller>=6.0" numpy scipy networkx >/dev/null
# Make erh_core importable for the freeze.
"$PY" -m pip install -e "$REPO_ROOT" >/dev/null 2>&1 || \
  echo "[sidecar] editable install skipped (using PYTHONPATH=$REPO_ROOT)"

# Windows (Git Bash) needs a native path and ';' separator for PYTHONPATH,
# otherwise Python never sees erh_core and PyInstaller's hidden imports fail.
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    REPO_ROOT_NATIVE="$(cygpath -w "$REPO_ROOT" 2>/dev/null || echo "$REPO_ROOT")"
    export PYTHONPATH="$REPO_ROOT_NATIVE;${PYTHONPATH:-}"
    ;;
  *)
    REPO_ROOT_NATIVE="$REPO_ROOT"
    export PYTHONPATH="$REPO_ROOT:${PYTHONPATH:-}"
    ;;
esac

"$PY" -m PyInstaller \
  --onefile \
  --name erh_sidecar \
  --paths "$REPO_ROOT_NATIVE" \
  --collect-submodules erh_core \
  --hidden-import numpy \
  --distpath dist \
  --workpath build \
  --specpath build \
  erh_sidecar.py

echo "[sidecar] built: $HERE/dist/"
ls -la dist || true
