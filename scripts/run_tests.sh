#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../backend"
python3 -m pytest tests/ -q
cd ../frontend
npm test
