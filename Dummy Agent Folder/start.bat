@echo off
REM ============================================================
REM  Inventory Management Agent - Windows Startup Script
REM ============================================================
REM  Starts the Flask API server and opens the frontend.
REM
REM  Usage:
REM     start.bat         Start API + open dashboard
REM     start.bat api      Start API only
REM     start.bat test     Run API test suite
REM     start.bat cli      Run CLI agent (no API)
REM ============================================================

setlocal
set "AGENT_DIR=%~dp0"
set "FRONTEND_DIR=%AGENT_DIR%..\Frontend"

echo.
echo ==================================================
echo   Inventory Management Agent - Startup
echo ==================================================
echo.

REM -- Create venv if needed --
if not exist "%AGENT_DIR%venv" (
    echo Creating Python virtual environment...
    python -m venv "%AGENT_DIR%venv"
    echo venv created.
) else (
    echo venv exists.
)

REM -- Install dependencies --
echo Installing dependencies...
call "%AGENT_DIR%venv\Scripts\pip.exe" install -r "%AGENT_DIR%requirements.txt" >nul 2>&1
echo Dependencies installed.

REM -- Determine action --
set "ACTION=%1"
if "%ACTION%"=="" set "ACTION=all"

if /i "%ACTION%"=="test" (
    echo Running API tests...
    call "%AGENT_DIR%venv\Scripts\python.exe" "%AGENT_DIR%test_api.py"
    goto :end
)

if /i "%ACTION%"=="cli" (
    echo Running CLI agent...
    call "%AGENT_DIR%venv\Scripts\python.exe" "%AGENT_DIR%agent.py"
    goto :end
)

if /i "%ACTION%"=="api" (
    echo Starting API server on http://localhost:5000
    call "%AGENT_DIR%venv\Scripts\python.exe" "%AGENT_DIR%api.py"
    goto :end
)

REM -- Default: start everything --
echo Starting API server on http://localhost:5000
start "Inventory Agent API" cmd /c "call "%AGENT_DIR%venv\Scripts\python.exe" "%AGENT_DIR%api.py""

echo Waiting for server to start...
timeout /t 3 /nobreak >nul

echo.
echo ==================================================
echo   Everything is running!
echo ==================================================
echo.
echo   API Server : http://localhost:5000
echo   Dashboard  : %FRONTEND_DIR%\index.html
echo.
echo   Tool pages:
echo     1. Order        - order.html
echo     2. Inventory    - inventory.html
echo     3. Payment      - payment.html
echo     4. Invoice      - invoice.html
echo     5. Delivery     - delivery.html
echo     6. Notification - notification.html
echo.

REM -- Open frontend in browser --
start "" "%FRONTEND_DIR%\index.html"

echo Frontend opened in your browser.
echo.
echo Close the API server window to stop.
echo.
pause

:end
endlocal
