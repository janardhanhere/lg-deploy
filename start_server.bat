@echo off
REM Windows batch script to start the lg-deploy FastAPI server

SETLOCAL
SET PYTHONPATH=%CD%

REM Allow host/port override
SET HOST=%LG_DEPLOY_HOST%
IF "%HOST%"=="" SET HOST=127.0.0.1
SET PORT=%LG_DEPLOY_PORT%
IF "%PORT%"=="" SET PORT=8000

REM Activate venv if present
IF EXIST .venv\Scripts\activate.bat (
    CALL .venv\Scripts\activate.bat
)

python start_server.py
