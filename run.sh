#!/usr/bin/env bash

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

# Import user's graphical session environment
if [ -f "$XDG_RUNTIME_DIR/environment" ]; then
    source "$XDG_RUNTIME_DIR/environment"
fi


source "$APP_DIR/.venv/bin/activate"
python3 "$APP_DIR/app.py"