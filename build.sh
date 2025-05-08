#!/bin/bash
pip3 install -r requirements.txt
python3 -m PyInstaller --onefile src/main.py
tar -czf module.tar.gz run.sh requirements.txt src meta.json build.sh setup.sh reload.sh