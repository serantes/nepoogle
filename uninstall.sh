#!/bin/sh
#
# Nepoogle user uninstalation script.
#

echo -n "Uninstalling Nepoogle..."

PROGRAMNAME=nepoogle
BINDIR=~/bin
BINNAME=$PROGRAMNAME
DESKTOPDIR=~/.local/share/applications/
ICONSDIR=~/.local/share/icons/hicolor/32x32/status/
ICONS="no_cover.png no_photo.png no_symbol.png no_video_thumbnail.png rating_empty.png rating_full.png rating_half.png"

#rm "$BINDIR"/"$BINNAME"

rm "$DESKTOPDIR"/$PROGRAMNAME.desktop

for icon in $ICONS; do
    rm "$ICONSDIR"/"$icon"
done

kbuildsycoca4 2> /dev/null

echo -e " done."
