#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${ROOT_DIR}/.venv"

if ! "${PYTHON_BIN}" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
then
  echo "Python 3.12 or newer is required for building." >&2
  exit 1
fi

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt

rm -rf build dist AppDir
pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name LongBookMerger \
  --paths src \
  --add-data "assets:assets" \
  --add-data "fonts:fonts" \
  --hidden-import PySide6.QtXml \
  src/main.py

appimage-builder --recipe appimage_builder.yml --skip-test
mkdir -p dist
if compgen -G "*.AppImage" > /dev/null; then
  mv ./*.AppImage dist/LongBookMerger.AppImage
fi
chmod +x dist/LongBookMerger.AppImage
echo "Built dist/LongBookMerger.AppImage"

