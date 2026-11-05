#!/bin/sh
# macOS / Linux: first run creates .venv and installs packages, then opens the app
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -r requirements.txt; }
.venv/bin/python launcher.py
