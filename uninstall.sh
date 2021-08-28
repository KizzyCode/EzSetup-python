#!/bin/sh

INSTALLPATH="$PREFIX/bin/ezsetup"
if test -f "$INSTALLPATH"; then
    rm -v "$INSTALLPATH"
fi