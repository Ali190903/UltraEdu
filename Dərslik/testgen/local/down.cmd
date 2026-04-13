@echo off
REM Stop TestGen containers (Windows). Data is preserved.
cd /d "%~dp0\.."
docker compose down
echo.
echo Stopped. Data preserved. Restart with: local\up.cmd
