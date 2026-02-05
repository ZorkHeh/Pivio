import os
from pathlib import Path

WORKSHOP_PATHS = [
    os.path.expanduser("~/.steam/debian-installation/steamapps/workshop/content/431960"),
    os.path.expanduser("~/.local/share/Steam/steamapps/workshop/content/431960"),
    os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/workshop/content/431960"),
]

VALID_VIDEO_EXTENSIONS: list[str] = ['.mp4', '.webm']
PREVIEW_EXTENSIONS: list[str] = ['preview.jpg', 'preview.png', 'preview.gif', 'preview.jpeg']

SERVICE_SCRIPT: str = os.path.abspath('pivio-autostart.sh')
SERVICE_NAME: str = 'vwallppaper-autostart.service'
SERVICE_PATH: Path =  Path.home() / '.config/systemd/user' / SERVICE_NAME
SERVICE_TEMPLATE_PATH: Path = Path("pivio.service.template")

STATE_FILE = Path.home() / ".config" / "wallpaper-manager" / "current.txt"
VOLUME_FILE = Path.home() / ".config" / "wallpaper-manager" / "volume.txt"