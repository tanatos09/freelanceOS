@echo off
REM Coverage script for Windows
REM This script runs the test suite with coverage measurement
REM Usage: run_coverage.bat

echo [*] Running coverage measurement...
echo.

REM Run coverage
coverage run --source='.' manage.py test users 2>&1 | tee coverage_test.log

echo.
echo [*] Generating coverage report...
coverage report -m --include="users/*" 2>&1 | tee coverage_report.txt

echo.
echo [*] Generating HTML coverage report...
coverage html --include="users/*"

echo.
echo [+] Coverage measurement complete!
echo [+] Text report: coverage_report.txt
echo [+] HTML report: htmlcov/index.html
