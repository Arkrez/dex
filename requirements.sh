#!/bin/bash
set -e

sudo apt update
sudo apt install -y \
    python3-venv python3-pip \
    libatlas-base-dev \
    libcamera-apps \
    python3-picamera2 \   # <-- add this for rpicam (Picamera2)
    git

# fresh venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

# pin numpy 1.26 for ABI match with tflite-runtime
pip install "numpy==1.26.4" "tflite-runtime==2.14.0" \
    pillow pygame gpiozero RPi.GPIO
