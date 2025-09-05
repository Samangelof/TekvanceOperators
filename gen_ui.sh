#!/bin/bash
SRC="./operators/gui/views"
DST="./operators/gui/modules"

for ui in $SRC/*.ui; do
    base=$(basename "$ui" .ui)
    pyuic5 "$ui" -o "$DST/${base}_ui.py"
    echo "✔ $base.ui → ${base}_ui.py"
done

read -p "Press [Enter] to exit..."