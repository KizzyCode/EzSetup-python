#!/bin/sh

INSTALLPATH="$PREFIX/bin/ezsetup"
if test -f "$INSTALLPATH";
    rm -v "$INSTALLPATH"
fi