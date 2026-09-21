#!/usr/bin/env bash
set -e

python -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
pip install git+https://github.com/SWivid/F5-TTS.git
pip install -r requirements.txt

echo "Setup complete. Copy .env.example to .env, add HF_TOKEN, then run: python app.py"
