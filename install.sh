#!/bin/sh
#
# Nepoogle user instalation script.
#

echo -n "Installing Nepoogle..."

PROGRAMNAME=nepoogle
BINDIR=~/bin
BINNAME=$PROGRAMNAME
DESKTOPDIR=~/.local/share/applications/
ICONSDIR=~/.local/share/icons/hicolor/32x32/status/
ICONS="no_cover.png no_photo.png no_symbol.png no_video_thumbnail.png rating_empty.png rating_full.png rating_half.png"

if ! [[ -d "$BINDIR" ]]; then
  mkdir -p "$BINDIR"
fi

if ! [[ -d "$ICONSDIR" ]]; then
  mkdir -p "$ICONSDIR"
fi

cp $BINNAME "$BINDIR"/"$BINNAME"
chmod +x "$BINDIR"/"$BINNAME"

cp $PROGRAMNAME.desktop "$DESKTOPDIR"/$PROGRAMNAME.desktop

for icon in $ICONS; do
    cp icons/"$icon" "$ICONSDIR"/"$icon"
done

kbuildsycoca4 2> /dev/null

echo -e " done."
