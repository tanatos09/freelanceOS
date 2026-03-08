#!/bin/bash
# E2E tests script for Linux/macOS using Playwright
# Usage: bash scripts/run_e2e.sh

set -e

echo "[*] Starting E2E test server..."
# Start Django development server in background
python manage.py runserver 8000 > server.log 2>&1 &
SERVER_PID=$!

echo "[*] Waiting for server to start..."
sleep 3

echo "[*] Running E2E tests with Playwright..."
echo ""

# Run E2E tests
python -m pytest e2e/test_auth_flow.py -v --tb=short 2>&1 | tee e2e_report.txt

echo ""
echo "[+] E2E test execution complete!"
echo "[+] Report: e2e_report.txt"
echo "[*] Killing test server (PID: $SERVER_PID)"

# Kill server
kill $SERVER_PID || true

echo "[+] Done!"
