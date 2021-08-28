#!/bin/sh

SOURCE="src/ezsetup.py"
INSTALLPATH="$PREFIX/bin/ezsetup"
install -v -m 0755 "$SOURCE" "$INSTALLPATH"