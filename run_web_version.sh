#!/bin/bash

echo "🎵 Starting GIF BPM Sync Tool - Web Version"
echo "============================================="
echo ""
echo "Opening web browser to http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the web server
cd gif-bpm-sync-web
python3 -m http.server 8000 