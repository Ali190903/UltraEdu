@echo off
REM Tail all testgen-prefixed log lines (retrieval, validation, variant).
cd /d "%~dp0\.."
docker compose logs -f backend
