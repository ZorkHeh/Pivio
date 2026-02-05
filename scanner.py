import os
import json
from dataclasses import dataclass

from config import WORKSHOP_PATHS, VALID_VIDEO_EXTENSIONS, PREVIEW_EXTENSIONS


@dataclass
class Wallpaper:
    """Represents a single wallpaper from Steam Workshop"""
    title: str
    file_path: str
    preview_path: str | None
    folder_path: str
    wallpaper_type: str  # 'video', 'scene', 'web', 'image'


class WallpaperScanner:
    """Scans Steam Workshop directory for Wallpaper Engine wallpapers"""
    workshop_paths = WORKSHOP_PATHS
    valid_video_extensions = VALID_VIDEO_EXTENSIONS
    valid_preview_extensions = PREVIEW_EXTENSIONS

    @classmethod
    def get_workshop_path(cls) -> None | str:
        """Find which Steam Workshop path exists on this system"""
        for workshop_path in cls.workshop_paths:
            if os.path.isdir(workshop_path):
                return workshop_path
        else:
            return None

    @classmethod
    def find_preview(cls, folder_path: str) -> None | str:
        """Look for preview image in multiple formats"""
        preview_files = os.listdir(folder_path)
        for preview_file in preview_files:
            if preview_file in cls.valid_preview_extensions:
                return os.path.join(folder_path, preview_file)
        else:
            return None

    @classmethod
    def parse_project_json(cls, folder_path: str) -> None | dict:
        """Parse the project.json file in a wallpaper folder"""
        project_json_path = os.path.join(folder_path, "project.json")

        if os.path.exists(project_json_path):
            with open(project_json_path, "r", encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                    return json_data
                except (json.JSONDecodeError, IOError):
                    return None
        else:
            return None

    @classmethod
    def scan(cls, filter_videos_only: bool = True) -> list[Wallpaper]:
        """
        Scans Workshop folders
        :param filter_videos_only: if True skips non-video types
        :return: list Wallpaper objects
        """
        wallpapers = []
        workshop_path = cls.get_workshop_path()

        if not workshop_path:
            return wallpapers

        for wallpaper_folder in os.listdir(workshop_path):

            project_json = cls.parse_project_json(os.path.join(workshop_path, wallpaper_folder))
            wallpaper_folder_path = os.path.join(workshop_path, wallpaper_folder)

            if not project_json:
                continue

            title = project_json.get('title')
            file_name = project_json.get('file')
            wallpaper_type = project_json.get('type')

            if filter_videos_only:
                # Skip non-video types
                if wallpaper_type.lower() in ['scene', 'web']:
                    continue

                # Check file extension
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext not in cls.valid_video_extensions:
                    continue

            full_file_path = os.path.join(workshop_path, wallpaper_folder, file_name)

            if not os.path.isfile(full_file_path):
                continue

            preview = cls.find_preview(wallpaper_folder_path)

            wallpapers.append(Wallpaper(
                title=title,
                file_path=full_file_path,
                preview_path=preview,
                folder_path=wallpaper_folder_path,
                wallpaper_type=wallpaper_type
            ))

        # Sort by title
        wallpapers.sort(key=lambda w: w.title.lower())

        return wallpapers


if __name__ == "__main__":
    from pprint import pprint

    pprint(WallpaperScanner.scan(filter_videos_only=True))
