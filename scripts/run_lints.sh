#!/bin/bash
# Linting script for Linux/macOS
# Usage: bash scripts/run_lints.sh

set -e

echo "[*] Running isort (import sorting)..."
python -m isort . --check-only --diff || {
    echo "[!] isort: Found issues (run without --check-only to fix)"
}

echo ""
echo "[+] isort check complete"

echo ""
echo "[*] Running flake8 (linting)..."
python -m flake8 . 2>&1 | tee lint_report.txt

echo ""
echo "[+] Linting complete!"
echo "[+] Report: lint_report.txt"
