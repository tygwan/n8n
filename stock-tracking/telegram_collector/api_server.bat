@echo off
echo ========================================
echo   Telegram Collector API Server
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

REM API 서버 실행
echo Starting API Server...
echo API Docs: http://localhost:8000/docs
echo.

python api.py

pause
