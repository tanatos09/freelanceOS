@echo off
REM Linting script for Windows
REM Usage: run_lints.bat

echo [*] Running isort (import sorting)...
C:/Users/frank/Desktop/freelanceos/venv/Scripts/python.exe -m isort . --check-only --diff

if %ERRORLEVEL% EQU 0 (
    echo [+] isort: OK
) else (
    echo [!] isort: Found issues (run without --check-only to fix)
)

echo.
echo [*] Running flake8 (linting)...
C:/Users/frank/Desktop/freelanceos/venv/Scripts/python.exe -m flake8 . 2>&1 | Tee-Object -FilePath lint_report.txt

echo.
echo [+] Linting complete!
echo [+] Report: lint_report.txt
