@echo off
echo ========================================
echo   Telegram Collector
echo ========================================
echo.

REM 가상환경 확인
if not exist ".venv" (
    echo Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM 가상환경 활성화
call .venv\Scripts\activate.bat

REM 수집기 실행
echo Starting Telegram Collector...
echo Press Ctrl+C to stop.
echo.
python collector.py

pause
