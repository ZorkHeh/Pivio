# Wallpaper Engine Linux Parser

A lightweight tool designed to parse video-type wallpapers from your local **Wallpaper Engine** storage and set them as your desktop background using **mpvpaper**.

## Requirements

Before running the setup, ensure you have the following installed on your system:

* **Python 3**: You must have `python3-venv` and `python3-pip` installed.
* [**mpvpaper**](https://github.com/GhostNaN/mpvpaper): This is required to render the video files to your desktop.

In case of having problems with dependencies during the installation of [**mpvpaper**](https://github.com/GhostNaN/mpvpaper), the following installation may help:
```bash
sudo apt install meson ninja-build wayland-protocols libwayland-dev libegl-dev libmpv-dev
```

## Installation & Setup

There are scripts to automate the environment setup and execution.

### Build the Project
Run the build script to automatically set up the virtual environment and attempt to create a system shortcut.
```bash
./build.sh
```

### Run the App

```bash
./run.sh
```

If you got permission denied while trying to run the scripts, run th following command to grant them executable permissions:
```bash
chmod +x run.sh build.sh
```

## LICENCE
This project is licensed under the MIT License.
