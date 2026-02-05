"""
Wallpaper Manager - PyQt6 GUI
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QPushButton, QSlider,
    QFrame, QMessageBox, QLineEdit
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from config import STATE_FILE
from scanner import WallpaperScanner, Wallpaper

from system import apply_wallpaper, SystemdManager, save_volume, get_volume


def save_current_wallpaper(path: str):
    """Save current wallpaper path to state file"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(path)


def get_current_wallpaper() -> Optional[str]:
    """
    Get the currently running wallpaper path.
    Returns None if no wallpaper is set or service isn't running.
    """

    # from system import SystemdManager
    status = SystemdManager.get_service_status()
    if not status['active']:
        return None

    if STATE_FILE.exists():
        path = STATE_FILE.read_text().strip()
        if path and Path(path).exists():
            return path
    return None


def clear_current_wallpaper():
    """Clear the saved current wallpaper"""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


# ============================================================
# DARK THEME STYLESHEET
# ============================================================
DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #111827;
    color: #f3f4f6;
}

QListWidget {
    background-color: #111827;
    border: none;
    border-right: 1px solid #1f2937;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1f2937;
    min-height: 50px;
}

QListWidget::item:hover {
    background-color: #1f2937;
}

QListWidget::item:selected {
    background-color: #3b82f6;
    color: white;
}

QPushButton {
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
    border: none;
}

QPushButton#applyBtn {
    background-color: #2563eb;
    color: white;
}

QPushButton#applyBtn:hover {
    background-color: #1d4ed8;
}

QPushButton#applyBtn:pressed {
    background-color: #1e40af;
}

QPushButton#stopBtn {
    background-color: #374151;
    color: white;
}

QPushButton#stopBtn:hover {
    background-color: #4b5563;
}

QPushButton#stopBtn:pressed {
    background-color: #1f2937;
}

QPushButton#refreshBtn {
    background-color: transparent;
    color: #9ca3af;
    font-size: 18px;
    padding: 4px;
    border: none;
}

QPushButton#refreshBtn:hover {
    color: #f3f4f6;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #374151;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #3b82f6;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: #3b82f6;
    border-radius: 3px;
}

QLabel#titleLabel {
    font-size: 16px;
    font-weight: 600;
}

QLabel#pathLabel {
    color: #9ca3af;
    font-size: 12px;
}

QLineEdit#pathEdit:focus {
    background-color: #1f2937;
    border-radius: 4px;
    padding: 2px 4px;
}

QLabel#sidebarTitle {
    font-size: 14px;
    font-weight: 600;
}

QFrame#previewFrame {
    background-color: #000000;
    border: none;
}

QFrame#controlsFrame {
    background-color: #111827;
    border-top: 1px solid #1f2937;
}
"""


class WallpaperListWidget(QListWidget):
    """Custom list widget for wallpapers with thumbnails"""

    THUMB_SIZE = QSize(80, 45)  # 16:9 aspect ratio

    def __init__(self):
        super().__init__()
        self.setIconSize(self.THUMB_SIZE)
        self.setSpacing(4)

    def add_wallpaper(self, wallpaper: Wallpaper, is_current: bool = False):
        """Add a wallpaper with thumbnail to the list"""
        # Show indicator if this is the running wallpaper
        display_name = f"● {wallpaper.title}" if is_current else wallpaper.title

        item = QListWidgetItem(display_name)
        item.setData(Qt.ItemDataRole.UserRole, wallpaper)

        # Set green color for running wallpaper
        if is_current:
            item.setForeground(Qt.GlobalColor.green)

        # Load thumbnail
        if wallpaper.preview_path and Path(wallpaper.preview_path).exists():
            pixmap = QPixmap(wallpaper.preview_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.THUMB_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                item.setIcon(QIcon(scaled))
        else:
            # Dark placeholder
            placeholder = QPixmap(self.THUMB_SIZE)
            placeholder.fill(Qt.GlobalColor.darkGray)
            item.setIcon(QIcon(placeholder))

        self.addItem(item)
        return item

    def get_selected(self) -> Optional[Wallpaper]:
        """Get currently selected wallpaper"""
        item = self.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None


class PreviewWidget(QFrame):
    """Video preview area - NO AUDIO"""

    def __init__(self):
        super().__init__()
        self.setObjectName("previewFrame")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: black;")

        # Media player - MUTED
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.audio.setVolume(0)  # Always muted
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)

        # Placeholder label
        self.placeholder = QLabel("Select a wallpaper")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #6b7280; font-size: 14px;")

        layout.addWidget(self.placeholder)
        layout.addWidget(self.video_widget)
        self.video_widget.hide()

    def load_video(self, path: str):
        """Load and play a video for preview"""
        # Stop and release previous video to free GPU memory
        self.player.stop()
        self.player.setSource(QUrl())

        self.placeholder.hide()
        self.video_widget.show()
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

    def stop(self):
        """Stop playback and show placeholder"""
        self.player.stop()
        self.player.setSource(QUrl())
        self.video_widget.hide()
        self.placeholder.show()


class ControlsWidget(QFrame):
    """Bottom controls panel"""

    def __init__(self):
        super().__init__()
        self.setObjectName("controlsFrame")
        self.setFixedHeight(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Title
        self.title_label = QLabel("No wallpaper selected")
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)

        # Path - selectable/copyable, wraps to multiple lines
        self.path_label = QLabel("")
        self.path_label.setObjectName("pathLabel")
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.path_label.setCursor(Qt.CursorShape.IBeamCursor)
        layout.addWidget(self.path_label)

        # Spacer
        layout.addSpacing(4)

        # Volume row
        volume_row = QHBoxLayout()
        volume_row.setSpacing(12)

        volume_label = QLabel("Volume")
        volume_label.setFixedWidth(50)
        volume_row.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        volume_row.addWidget(self.volume_slider)

        self.volume_value = QLabel("50%")
        self.volume_value.setFixedWidth(40)
        self.volume_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        volume_row.addWidget(self.volume_value)

        layout.addLayout(volume_row)

        # Spacer
        layout.addSpacing(4)

        # Buttons row - fixed size, won't compress
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setObjectName("applyBtn")
        self.apply_btn.setFixedSize(100, 36)
        btn_row.addWidget(self.apply_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedSize(100, 36)
        btn_row.addWidget(self.stop_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def set_wallpaper_info(self, title: str, path: str):
        """Update displayed wallpaper info"""
        self.title_label.setText(title)
        self.path_label.setText(path)


class SidebarWidget(QWidget):
    """Left sidebar with wallpaper list"""

    def __init__(self):
        super().__init__()
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet("border-bottom: 1px solid #1f2937;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 12, 0)

        title = QLabel("Wallpapers")
        title.setObjectName("sidebarTitle")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setObjectName("refreshBtn")
        self.refresh_btn.setFixedSize(28, 28)
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setToolTip("Refresh wallpaper list")
        header_layout.addWidget(self.refresh_btn)

        layout.addWidget(header)

        # List
        self.list_widget = WallpaperListWidget()
        layout.addWidget(self.list_widget)

    def add_wallpaper(self, wallpaper: Wallpaper, is_current: bool = False) -> QListWidgetItem:
        """Add a wallpaper to the list"""
        return self.list_widget.add_wallpaper(wallpaper, is_current)

    def clear(self):
        """Clear the list"""
        self.list_widget.clear()

    def get_selected(self) -> Optional[Wallpaper]:
        """Get currently selected wallpaper"""
        return self.list_widget.get_selected()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wallpaper Manager")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self.current_wallpaper: Optional[Wallpaper] = None
        self.running_wallpaper_path: Optional[str] = None

        self._setup_ui()
        self._connect_signals()
        self._load_wallpapers()
        self._load_saved_volume()

    def _load_saved_volume(self):
        """Load saved volume setting"""
        volume = get_volume()
        self.controls.volume_slider.setValue(volume)

    def _setup_ui(self):
        """Build the UI"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = SidebarWidget()
        layout.addWidget(self.sidebar)

        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Preview
        self.preview = PreviewWidget()
        right_layout.addWidget(self.preview, 1)

        # Controls
        self.controls = ControlsWidget()
        right_layout.addWidget(self.controls)

        layout.addWidget(right_panel, 1)

    def _connect_signals(self):
        """Connect UI signals to handlers"""
        self.sidebar.list_widget.currentItemChanged.connect(self._on_wallpaper_selected)
        self.sidebar.refresh_btn.clicked.connect(self._load_wallpapers)

        self.controls.volume_slider.valueChanged.connect(self._on_volume_changed)
        self.controls.apply_btn.clicked.connect(self._on_apply)
        self.controls.stop_btn.clicked.connect(self._on_stop)

    def _load_wallpapers(self):
        """Scan and load wallpapers using WallpaperScanner"""
        self.sidebar.clear()

        # Get currently running wallpaper
        self.running_wallpaper_path = get_current_wallpaper()

        # Scan for wallpapers
        wallpapers = WallpaperScanner.scan(filter_videos_only=True)

        if not wallpapers:
            workshop_path = WallpaperScanner.get_workshop_path()
            if not workshop_path:
                QMessageBox.warning(
                    self,
                    "Wallpaper Engine Not Found",
                    "Could not find Wallpaper Engine workshop folder.\n\n"
                    "Make sure Wallpaper Engine is installed via Steam."
                )
            return

        # Add to list
        for wallpaper in wallpapers:
            is_current = (
                    self.running_wallpaper_path is not None
                    and wallpaper.file_path == self.running_wallpaper_path
            )
            self.sidebar.add_wallpaper(wallpaper, is_current)

    def _on_wallpaper_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle wallpaper selection change"""
        if not current:
            return

        wallpaper = current.data(Qt.ItemDataRole.UserRole)
        if not wallpaper:
            return

        self.current_wallpaper = wallpaper

        # Update controls
        self.controls.set_wallpaper_info(wallpaper.title, wallpaper.file_path)

        # Load preview
        self.preview.load_video(wallpaper.file_path)

    def _on_volume_changed(self, value: int):
        """Handle volume slider change - only saves to config"""
        self.controls.volume_value.setText(f"{value}%")
        save_volume(value)

    def _on_apply(self):
        """Apply the selected wallpaper"""
        if not self.current_wallpaper:
            QMessageBox.warning(self, "No Selection", "Please select a wallpaper first.")
            return

        success = apply_wallpaper(self.current_wallpaper.file_path)

        if success:
            # Save state and refresh list to update indicators
            save_current_wallpaper(self.current_wallpaper.file_path)
            self._load_wallpapers()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to apply wallpaper. Check the logs."
            )

    def _on_stop(self):
        """Stop the wallpaper service (NOT the preview!)"""
        SystemdManager.stop_service()
        SystemdManager.disable_service()

        # Clear state and refresh list
        clear_current_wallpaper()
        self._load_wallpapers()

    def closeEvent(self, event):
        """Clean up on close"""
        self.preview.stop()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
