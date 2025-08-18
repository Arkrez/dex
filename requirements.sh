#!/bin/bash
set -e

sudo apt update
sudo apt install -y python3-venv python3-pip libatlas-base-dev libcamera-apps git

# fresh venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# tooling
python -m pip install --upgrade pip setuptools wheel

# >>> critical: pin numpy 1.26, then tflite-runtime 2.14 <<<
pip install "numpy==1.26.4" "tflite-runtime==2.14.0" pillow pygame gpiozero RPi.GPIO

# quick sanity check (should print version & not crash)
python - <<'PY'
import numpy, tflite_runtime.interpreter as t
print("NumPy:", numpy.__version__)
t.Interpreter  # existence check
print("tflite ok")
PY

echo "All set. Run: source .venv/bin/activate"
