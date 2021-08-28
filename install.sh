#!/bin/sh

SOURCE="src/ezsetup.py"
INSTALLPATH="$PREFIX/bin/ezsetup"
install -v -o root -m 0755 "$SOURCE" "$INSTALLPATH"