#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DIST_DIR="$SCRIPT_DIR/ejecutable"
WORK_DIR="$SCRIPT_DIR/temp-pyinstaller"
EXE_PATH="$DIST_DIR/control-monotributistas"

rm -rf "$WORK_DIR"
mkdir -p "$DIST_DIR" "$WORK_DIR"

if [ -f "$EXE_PATH" ]; then
  rm -f "$EXE_PATH"
fi

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python is not available in PATH." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -m PyInstaller --version >/dev/null 2>&1; then
  echo "PyInstaller is not installed. Install it with 'pip install pyinstaller'." >&2
  exit 1
fi

"$PYTHON_BIN" -m PyInstaller gui.py \
  --onefile \
  --windowed \
  --name control-monotributistas \
  --icon "$SCRIPT_DIR/lib/ABP.ico" \
  --distpath "$DIST_DIR" \
  --workpath "$WORK_DIR" \
  --specpath "$WORK_DIR" \
  --noconfirm \
  --clean

mkdir -p "$DIST_DIR/lib"
shopt -s nullglob
for asset in "$SCRIPT_DIR"/lib/*.png "$SCRIPT_DIR"/lib/*.ico; do
  cp "$asset" "$DIST_DIR/lib/"
done
shopt -u nullglob

echo "Executable created in $DIST_DIR"
echo "Temporary build files stored in $WORK_DIR"
