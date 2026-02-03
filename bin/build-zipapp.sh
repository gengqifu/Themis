#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_BASE="${ROOT_DIR}/build"
BUILD_DIR="${BUILD_BASE}/pyz"
DIST_DIR="${ROOT_DIR}/dist"
mkdir -p "${BUILD_BASE}"
VENV_DIR="$(mktemp -d "${BUILD_BASE}/venv.XXXXXX")"
trap 'rm -rf "${VENV_DIR}"' EXIT

rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"

python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip
"${VENV_DIR}/bin/python" -m pip install -r "${ROOT_DIR}/requirements.txt" -t "${BUILD_DIR}"
cp -R "${ROOT_DIR}/themis" "${BUILD_DIR}/themis"

python3 -m zipapp "${BUILD_DIR}" \
  -m "themis.__main__:main" \
  -p "/usr/bin/env python3" \
  -o "${DIST_DIR}/themis.pyz"

echo "Built ${DIST_DIR}/themis.pyz"
