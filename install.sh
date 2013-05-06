#!/bin/sh
#
# Nepoogle user instalation script.
#

echo -n "Installing Nepoogle..."

PROGRAMNAME=nepoogle
BINDIR=~/bin
BINNAME=$PROGRAMNAME
DESKTOPDIR=~/.local/share/applications
ICONSDIR=~/.local/share/icons/hicolor
ICONS32="rating_empty.png rating_full.png rating_half.png"
ICONS48="orientation_1.png orientation_2.png orientation_3.png orientation_4.png orientation_5.png orientation_6.png orientation_7.png orientation_8.png sparql.png"
ICONS128="no_cover.png no_photo.png no_symbol.png no_video_thumbnail.png"

if ! [ -d "$BINDIR" ]; then
  mkdir -p "$BINDIR"
fi

if ! [ -d "$DESKTOPDIR" ]; then
  mkdir -p "$DESKTOPDIR"
fi

if ! [ -d "$ICONSDIR"/32x32/status/ ]; then
  mkdir -p "$ICONSDIR"/32x32/status/
fi

if ! [ -d "$ICONSDIR"/48x48/status/ ]; then
  mkdir -p "$ICONSDIR"/48x48/status/
fi

if ! [ -d "$ICONSDIR"/128x128/status/ ]; then
  mkdir -p "$ICONSDIR"/128x128/status/
fi

cp $BINNAME "$BINDIR"/"$BINNAME"
chmod +x "$BINDIR"/"$BINNAME"

cp $PROGRAMNAME.desktop "$DESKTOPDIR"/$PROGRAMNAME.desktop

for icon in $ICONS32; do
    cp icons/"$icon" "$ICONSDIR"/32x32/status/"$icon"
done

for icon in $ICONS48; do
    cp icons/"$icon" "$ICONSDIR"/48x48/status/"$icon"
done

for icon in $ICONS128; do
    cp icons/"$icon" "$ICONSDIR"/128x128/status/"$icon"
done

kbuildsycoca4 2> /dev/null

echo -e " done."
