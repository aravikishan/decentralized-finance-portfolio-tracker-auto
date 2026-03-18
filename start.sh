#!/bin/bash
set -e
echo "Starting Decentralized Finance Portfolio Tracker..."
uvicorn app:app --host 0.0.0.0 --port 9003 --workers 1
