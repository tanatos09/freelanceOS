@echo off
REM E2E tests script for Windows using Playwright
REM Usage: run_e2e.bat

echo [*] Starting E2E test server...
REM Start Django development server in background
start /B cmd /c "C:/Users/frank/Desktop/freelanceos/venv/Scripts/python.exe manage.py runserver 8000 > server.log 2>&1"
set SERVER_PID=%errorlevel%

echo [*] Waiting for server to start...
timeout /t 3 /nobreak

echo [*] Running E2E tests with Playwright...
echo.

REM Run E2E tests
C:/Users/frank/Desktop/freelanceos/venv/Scripts/python.exe -m pytest e2e/test_auth_flow.py -v --tb=short 2>&1 | Tee-Object -FilePath e2e_report.txt

echo.
echo [+] E2E test execution complete!
echo [+] Report: e2e_report.txt
echo [+] Server will continue running (kill with Ctrl+C)
