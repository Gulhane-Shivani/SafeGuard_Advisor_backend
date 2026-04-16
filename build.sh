#!/usr/bin/env bash
# exit on error
set -o errexit

# Create a writable cargo directory to avoid "Read-only file system" errors
mkdir -p /opt/render/project/src/.cargo
export CARGO_HOME=/opt/render/project/src/.cargo

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
python -m pip install -r requirements.txt

# Run migrations if necessary (optional)
# python main.py --migrate
