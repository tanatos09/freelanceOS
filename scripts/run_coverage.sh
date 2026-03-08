#!/bin/bash
# Coverage script for Linux/macOS
# This script runs the test suite with coverage measurement
# Usage: bash scripts/run_coverage.sh

set -e

echo "[*] Running coverage measurement..."
echo ""

# Run coverage
coverage run --source='.' manage.py test users 2>&1 | tee coverage_test.log

echo ""
echo "[*] Generating coverage report..."
coverage report -m --include="users/*" 2>&1 | tee coverage_report.txt

echo ""
echo "[*] Generating HTML coverage report..."
coverage html --include="users/*"

echo ""
echo "[+] Coverage measurement complete!"
echo "[+] Text report: coverage_report.txt"
echo "[+] HTML report: htmlcov/index.html"
