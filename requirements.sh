#!/bin/bash
set -e

echo "=== Updating system and repos ==="
sudo apt update || true
sudo apt install -y raspberrypi-archive-keyring || true
echo "deb http://archive.raspberrypi.org/debian/ bookworm main" | \
  sudo tee /etc/apt/sources.list.d/raspi.list >/dev/null || true
sudo apt update
sudo apt full-upgrade -y

echo "=== Installing system packages ==="
sudo apt install -y \
    python3-venv python3-pip \
    libatlas-base-dev \
    libcamera-apps \
    python3-picamera2 \
    git

echo "=== Creating virtual environment (with system packages) ==="
rm -rf .venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

echo "=== Upgrading pip tools ==="
python -m pip install --upgrade pip setuptools wheel

echo "=== Installing Python packages via pip ==="
pip install "numpy==1.26.4" "tflite-runtime==2.14.0" \
    pillow pygame gpiozero RPi.GPIO

echo "=== Sanity check ==="
python - <<'PY'
import numpy, tflite_runtime.interpreter as t
print("NumPy:", numpy.__version__, "TFLite OK:", hasattr(t,'Interpreter'))
import picamera2
print("Picamera2 OK")
PY

echo "=== All set! To start using, run: source .venv/bin/activate ==="
