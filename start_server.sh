#!/bin/bash
# Unix shell script to start the lg-deploy FastAPI server

export PYTHONPATH="$(pwd)"

# Allow host/port override
HOST="${LG_DEPLOY_HOST:-127.0.0.1}"
PORT="${LG_DEPLOY_PORT:-8000}"

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

python3 start_server.py
