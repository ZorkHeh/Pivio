#!/usr/bin/env bash
set -e

APP_NAME="Pivio"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
DESKTOP_FILE="$HOME/.local/share/applications/pivio.desktop"

echo "== Building $APP_NAME =="

# Python check
if ! command -v python3 >/dev/null; then
  echo "python3 not found"
  echo "Install it with:"
  echo "  sudo apt install python3"
  exit 1
fi

# venv check
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "python3-venv not installed"
  echo "Install it with:"
  echo "  sudo apt install python3-venv"
  exit 1
fi

# Create venv
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# pip check
if ! command -v pip >/dev/null; then
  echo "pip not available in venv"
  echo "Try:"
  echo "  sudo apt install python3-pip"
  exit 1
fi

# Install deps
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Desktop shortcut
echo "Creating desktop shortcut..."

mkdir -p "$(dirname "$DESKTOP_FILE")"


cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Exec=/usr/bin/env bash -c '$APP_DIR/run.sh'
Type=Application
Categories=Utility;
Terminal=false
EOF

chmod +x "$DESKTOP_FILE"

echo "Build complete"
echo "You can now:"
echo "  • Run ./run.sh"
echo "  • Launch '$APP_NAME' from your app menu(BETA may not work)"
