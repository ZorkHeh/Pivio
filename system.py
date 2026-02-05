import os
import subprocess
from pathlib import Path

from config import SERVICE_PATH, SERVICE_TEMPLATE_PATH, SERVICE_SCRIPT, SERVICE_NAME, VOLUME_FILE


class SystemdManager:
    """Handles systemd service management"""

    service_path = SERVICE_PATH
    service_script = SERVICE_SCRIPT
    service_name = SERVICE_NAME
    service_template_path = SERVICE_TEMPLATE_PATH

    @staticmethod
    def get_service_path() -> Path:
        return SystemdManager.service_path

    @staticmethod
    def get_service_script_path() -> str:
        return SystemdManager.service_script

    @staticmethod
    def create_service(video_path: str) -> bool:
        """
        Creates service file that autostart mpvpaper on boot
        :param video_path: Full path to the video file
        :return: True if successful, False otherwise
        """
        service_path = SystemdManager.get_service_path()
        service_script_path = SystemdManager.get_service_script_path()

        # make script executable
        os.chmod(service_script_path, 0o755)

        # Create parent directories
        service_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            template = Path(SystemdManager.service_template_path).read_text()

            service = template.replace(
                "{{VIDEO_PATH}}",
                video_path
            )

            service = service.replace("{{SERVICE_SCRIPT_PATH}}", service_script_path)

            with open(service_path, "w") as f:
                f.write(service)
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def reload_daemon() -> bool:
        """Reload systemd daemon"""
        try:
            subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def enable_service() -> bool:
        """Enable the service to start automatically on login"""
        try:
            subprocess.run(['systemctl', '--user', 'enable', SystemdManager.service_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def disable_service() -> bool:
        """Disable the service from starting automatically"""
        try:
            subprocess.run(['systemctl', '--user', 'disable', SystemdManager.service_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(e)
            return False

    @staticmethod
    def start_service() -> bool:
        """Start the service immediately"""
        try:
            subprocess.run(['systemctl', '--user', 'start', SystemdManager.service_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(e)
            return False

    @staticmethod
    def stop_service() -> bool:
        """Stop the running service"""
        try:
            subprocess.run(['systemctl', '--user', 'stop', SystemdManager.service_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(e)
            return False

    @staticmethod
    def get_service_status() -> dict:
        """
        Get the service status

        :return: dict with keys:
            - 'active': bool - whether service is running
            - 'enabled': bool - whether service starts on boot
            - 'status': str - raw status string (active, inactive, failed, etc.)
        """
        result = {
            'active': False,
            'enabled': False,
            'status': 'unknown'
        }

        try:
            # Check if active
            active_check = subprocess.run(
                ['systemctl', '--user', 'is-active', SystemdManager.service_name],
                capture_output=True,
                text=True
            )
            result['status'] = active_check.stdout.strip()
            result['active'] = active_check.returncode == 0

            # Check if enabled (starts on boot)
            enabled_check = subprocess.run(
                ['systemctl', '--user', 'is-enabled', SystemdManager.service_name],
                capture_output=True,
                text=True
            )
            result['enabled'] = enabled_check.returncode == 0

        except Exception:
            pass

        return result


def apply_wallpaper(video_path: str) -> bool:
    """
    Applies wallpaper. Starts and enables wallpaper

    :param video_path: Full path to video

    :return: True if successful, False otherwise
    """
    SystemdManager.stop_service()

    if not SystemdManager.create_service(video_path):
        return False

    SystemdManager.reload_daemon()

    if not SystemdManager.enable_service():
        return False

    if not SystemdManager.start_service():
        return False

    return True


def save_volume(volume: int) -> bool:
    """
    Save volume to a config file
    :param volume: 0-100
    :return: True if successful, False otherwise
    """
    try:
        VOLUME_FILE.parent.mkdir(parents=True, exist_ok=True)
        VOLUME_FILE.write_text(str(volume))
        return True
    except Exception as e:
        print(f"Failed to save volume: {e}")
        return False


def get_volume() -> int:
    """
    Reads config value of volume
    :return: volume
    """
    try:
        if VOLUME_FILE.exists():
            return int(VOLUME_FILE.read_text().strip())
    except (ValueError, OSError):
        pass
    return 50
