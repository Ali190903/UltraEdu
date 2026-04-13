@echo off
REM Verify RAG corpus is populated.
cd /d "%~dp0\.."
docker compose exec backend python scripts/qdrant_health.py
echo.
echo For topic breakdown:
echo   docker compose exec backend python scripts/qdrant_health.py --subject math --grade 11
