@echo off
REM Clean restart when things get weird. Keeps DB + qdrant data.
cd /d "%~dp0\.."
echo Stopping containers...
docker compose down
echo Rebuilding images (no cache)...
docker compose build --no-cache
echo Starting fresh...
docker compose up -d
echo.
echo Done. Check: docker compose ps
