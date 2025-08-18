#!/bin/bash
set -e

echo "Updating system..."
sudo apt update
sudo apt install -y \
    python3-pip python3-venv \
    libatlas-base-dev \
    libcamera-apps \
    git

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Upgrading pip..."
python3 -m pip install --upgrade pip setuptools wheel
python3 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
pip install "tflite-runtime==2.14.0"   # pulls cp311 manylinux aarch64 wheel


echo "Installing Python packages..."
python3 -m pip install \
    pygame \
    numpy \
    pillow \
    gpiozero \
    RPi.GPIO \
    --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime

echo "All dependencies installed."
echo "To start using, run: source .venv/bin/activate"
