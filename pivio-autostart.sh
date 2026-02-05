#!/bin/bash

VOLUME_FILE="$HOME/.config/wallpaper-manager/volume.txt"
VOLUME=50

if [ -f "$VOLUME_FILE" ]; then
    VOLUME=$(cat "$VOLUME_FILE")
fi

exec mpvpaper \
  -o "--loop-file=inf --volume=$VOLUME --idle=yes --panscan=1.0" \
  '*' \
  "$1"