@echo off
setlocal

REM ============================================================
REM  Dashboard Launcher - double-click to run
REM
REM  Starts two local services and opens the dashboard in Edge:
REM    1) 8765 : static file server (serves the dashboard HTML)
REM    2) 9001 : state-server.py (CORS proxy + state sync)
REM
REM  Requires: Python 3.8+ (with pythonw.exe), Microsoft Edge
REM
REM  The Chinese filename in the URL is URL-encoded (ASCII-safe).
REM ============================================================

set "ROOT=%~dp0"
set "PORT=8765"
set "STATE_PORT=9001"
set "PAGE=http://127.0.0.1:%PORT%/%E9%93%BE%E6%8E%A5%E8%B7%B3%E8%BD%AC.html"

REM ---- Detect Python ----
where python >nul 2>nul
if not errorlevel 1 (
    set "PY_STATIC=pythonw"
    set "PY_STATE=python -u"
    goto :have_python
)
where py >nul 2>nul
if not errorlevel 1 (
    set "PY_STATIC=py -3"
    set "PY_STATE=py -3 -u"
    goto :have_python
)
echo [ERROR] Python not found. Install Python 3.8+ from https://www.python.org/downloads/
echo         (make sure to check "Add Python to PATH" during install)
pause
exit /b 1

:have_python

cd /d "%ROOT%"

echo ============================================================
echo  Dashboard Launcher
echo ============================================================
echo.

REM ---- Kill any stale processes on these ports (prevents "port in use" from previous run) ----
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R "[: ]%STATE_PORT%.*LISTENING"') do (
    echo [cleanup] killing stale process on port %STATE_PORT% (PID=%%P)
    taskkill /F /PID %%P >nul 2>&1
)
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R "[: ]%PORT%.*LISTENING"') do (
    echo [cleanup] killing stale process on port %PORT% (PID=%%P)
    taskkill /F /PID %%P >nul 2>&1
)

REM ---- Start static file server (pythonw - silent, no expected errors) ----
echo [1/2] Starting static file server on port %PORT%...
start /B %PY_STATIC% -m http.server %PORT% --bind 127.0.0.1

REM ---- Start state-server (python -u so any error is visible in this window) ----
echo [2/2] Starting state-server on port %STATE_PORT%...
start /B %PY_STATE% "%ROOT%state-server.py"

REM ---- Wait for state-server to be ready (poll up to 8 seconds) ----
echo        Waiting for state-server...
set /a retries=0
:wait_loop
timeout /t 1 /nobreak >nul
set /a retries+=1
curl -s -m 1 http://127.0.0.1:%STATE_PORT%/health >nul 2>&1
if not errorlevel 1 goto :state_ready
if %retries% GEQ 8 goto :state_failed
goto :wait_loop

:state_failed
echo.
echo ============================================================
echo  [FAILED] state-server did not respond within 8s.
echo           http://127.0.0.1:%STATE_PORT%/health is unreachable.
echo ============================================================
echo.
echo Troubleshooting:
echo   - Look ABOVE for Python tracebacks (errors)
echo   - Open Task Manager -> Details -> look for python.exe
echo   - If python.exe is running but 9001 is down = port conflict
echo   - If no python.exe at all = startup failed
echo.
echo Press any key to close...
pause >nul
exit /b 1

:state_ready
echo        [OK] state-server is ready

REM ---- Open Edge ----
where msedge >nul 2>nul
if not errorlevel 1 (
    start "" msedge.exe "%PAGE%"
) else (
    echo Edge not found, please open manually: %PAGE%
)

echo.
echo ============================================================
echo  All services started
echo ------------------------------------------------------------
echo   Dashboard:        %PAGE%
echo   Static server:    http://127.0.0.1:%PORT%/
echo   state-server:     http://127.0.0.1:%STATE_PORT%/health
echo ------------------------------------------------------------
echo   Close this window = stop all services
echo   Re-run this script to restart
echo ============================================================
echo.
echo Live logs below (state-server output will appear here):
echo ------------------------------------------------------------
pause
