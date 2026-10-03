@echo off
setlocal
echo ==============================================================
echo       Antigravity Chat Recovery - 1-Click Repair
echo ==============================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src"

python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python 3 is not found in your PATH.
    echo     Please install Python 3.8+ or run the standalone release .exe
    pause
    exit /b 1
)

python -m antigravity_restore.cli %*

echo.
echo Press any key to close this window...
pause >nul
