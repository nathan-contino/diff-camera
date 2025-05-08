#!/bin/bash
pip3 install -r requirements.txt
pyinstaller --onefile src/main.py --distpath dist --name main
tar -czf dist/archive.tar.gz dist/main meta.json