#!/bin/bash
set -euo pipefail

echo "Updating system..."
sudo apt update
sudo apt install -y python3-venv python3-pip libatlas-base-dev libcamera-apps git

cd "$(dirname "$0")"

echo "Creating venv..."
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

# Detect Python tag and arch
PYTAG=$(python - <<'PY'
import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")
PY
)
ARCH=$(uname -m)

echo "Detected: $PYTAG on $ARCH"

# Choose wheel URL from Coral repo (change version here if needed)
BASE="https://github.com/google-coral/pycoral/releases/download/release-frogfish"
case "$ARCH" in
  aarch64)
    WHEEL="tflite_runtime-2.14.0-${PYTAG}-${PYTAG}-linux_aarch64.whl"
    ;;
  armv7l)
    WHEEL="tflite_runtime-2.14.0-${PYTAG}-${PYTAG}-linux_armv7l.whl"
    ;;
  *)
    echo "Unsupported arch ($ARCH). Try: python -m pip install tflite-runtime"
    exit 1
    ;;
esac

URL="$BASE/$WHEEL"
echo "Installing TFLite Runtime from $URL ..."
python -m pip install --no-cache-dir "$URL"

echo "Installing project Python packages..."
python -m pip install pygame numpy pillow gpiozero RPi.GPIO

echo "Verifying tflite_runtime import..."
python - <<'PY'
import tflite_runtime.interpreter as tfl; print("OK:", tfl)
PY

echo "Done. Activate with:  source .venv/bin/activate"
