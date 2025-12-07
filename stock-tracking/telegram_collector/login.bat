@echo off
echo ========================================
echo   Telegram Login
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

REM 로그인 스크립트 실행
python login.py

pause
