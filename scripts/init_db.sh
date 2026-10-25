#!/usr/bin/env bash
# Create the SQLite database and load demo data.
set -e
cd "$(dirname "$0")/../backend"
python3 -m app.seed
