#!/bin/sh
cd `dirname $0`

# Create a virtual environment to run our code
VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"

if ! $PYTHON -m pip install pyinstaller -Uqq; then
    exit 1
fi

# Build the executable
$PYTHON -m PyInstaller --onefile \
    --hidden-import="googleapiclient" \
    src/main.py

# Create the module archive
rm -f dist/module.tar.gz
tar -czvf dist/module.tar.gz dist/main
