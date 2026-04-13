@echo off
REM Launch TestGen locally (Windows). Run from Dərslik\testgen\ folder.
cd /d "%~dp0\.."
echo [1/2] Building images if needed...
docker compose build
if errorlevel 1 goto :error

echo [2/2] Starting containers...
docker compose up -d
if errorlevel 1 goto :error

echo.
echo ==================================================
echo   frontend : http://localhost:3000
echo   backend  : http://localhost:8000/health
echo   qdrant   : http://localhost:6333/dashboard
echo ==================================================
echo.
echo Logs:  docker compose logs -f backend
echo Stop:  local\down.cmd
goto :eof

:error
echo.
echo !! Build or start failed. Check Docker Desktop and try:
echo    docker compose down
echo    local\up.cmd
exit /b 1
