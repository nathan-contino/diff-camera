#!/bin/bash
pip3 install -r requirements.txt
pip3 install pyinstaller
python3 -m PyInstaller --onefile --hidden-import="googleapiclient" src/main.py
tar -czvf dist/archive.tar.gz dist/main meta.json