#!/bin/sh
cd `dirname $0`

# Create a virtual environment to run our code
VENV_NAME="venv"
PYTHON="$VENV_NAME/bin/python"

if ! $PYTHON -m pip install pyinstaller -Uqq; then
    exit 1
fi

# Build for linux-arm64
$PYTHON -m PyInstaller --onefile \
    --hidden-import="googleapiclient" \
    --target-arch=arm64 \
    --target-platform=linux \
    src/main.py

# Create the module archive
rm -f module.tar.gz
tar -czvf module.tar.gz requirements.txt src/*.py src/models/*.py meta.json setup.sh reload.sh dist/main
