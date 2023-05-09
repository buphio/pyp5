#!/bin/zsh

# Shell script to create standalone macOS executable.
# Very specific, may need to be modified for general use.

if [ $# -lt 2 ]
then
    echo "installer: Missing arguments"
    echo "usage: "$0" [python_script] [target_architecture (x86_64, arm64, universal2)]"
    exit 1
fi

pyinstaller --onefile --clean --target-architecture "$2" "$1"

if [ $? -eq 1 ]; then
    echo "Compilation failed."
else
    mv dist/"$(basename "$1" .py)" .
    rm -rf __pycache__
    rm -rf build
    rm -rf dist
    rm "$(basename "$1" .py)".spec
fi
