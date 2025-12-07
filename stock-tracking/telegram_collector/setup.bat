@echo off
echo ========================================
echo   Telegram Collector Setup
echo ========================================
echo.

REM 가상환경 생성
if not exist ".venv" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
) else (
    echo [1/3] Virtual environment already exists.
)

REM 가상환경 활성화
echo [2/3] Activating virtual environment...
call .venv\Scripts\activate.bat

REM 의존성 설치
echo [3/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To run the collector:
echo   run.bat
echo.
pause
