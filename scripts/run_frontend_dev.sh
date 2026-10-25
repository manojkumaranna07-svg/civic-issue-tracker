#!/usr/bin/env bash
# Optional: Vite dev server with hot reload at http://localhost:5173.
# (Not needed for the demo - the backend serves the built app.)
set -e
cd "$(dirname "$0")/../frontend"
npm run dev
