#!/bin/bash
pip3 install -r requirements.txt
python3 -m PyInstaller --onefile src/main.py
tar -czvf dist/archive.tar.gz dist/main