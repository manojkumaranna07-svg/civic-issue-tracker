#!/usr/bin/env bash
# Serve API + built frontend at http://localhost:8000 (docs at /docs).
set -e
cd "$(dirname "$0")/../backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
