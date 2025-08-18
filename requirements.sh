#!/bin/bash
set -e

sudo apt update || true
sudo apt install -y raspberrypi-archive-keyring || true
echo "deb http://archive.raspberrypi.org/debian/ bookworm main" | sudo tee /etc/apt/sources.list.d/raspi.list >/dev/null
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y python3-venv python3-pip libatlas-base-dev libcamera-apps python3-picamera2 git

rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install "numpy==1.26.4" "tflite-runtime==2.14.0" pillow pygame gpiozero RPi.GPIO
python - <<'PY'
import tflite_runtime.interpreter as t, numpy, importlib
print("NumPy", numpy.__version__, "TFLite OK:", hasattr(t,'Interpreter'))
importlib.import_module('picamera2')
print("Picamera2 OK")
PY
echo "Done. Use: source .venv/bin/activate"
