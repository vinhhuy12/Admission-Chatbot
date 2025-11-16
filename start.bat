@echo off
chcp 65001 >nul
title UIT Admissions Chatbot - Advanced Launcher
color 0B

REM ============================================
REM Advanced Startup with Health Check
REM ============================================

set PYTHON_PATH=C:\Users\admin\miniconda3\envs\LGR\python.exe
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set MAX_RETRIES=3

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   UIT Admissions Chatbot - Advanced Startup           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Setup
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if not exist "logs" mkdir "logs"

REM Cleanup existing processes
echo [*] Cleaning up existing processes...
taskkill /F /FI "WINDOWTITLE eq UIT Chatbot*" >nul 2>&1
timeout /t 2 >nul

REM Start Backend in a new window
echo.
echo [1/2] Starting Backend API in a new window...
start "UIT Chatbot - Backend API" cmd /k "%PYTHON_PATH% run.py --mode single"

REM Start Frontend in a new window
echo.
echo [2/2] Starting Frontend in a new window...
start "UIT Chatbot - Frontend" cmd /k "cd frontend && npm run dev"

REM Final status
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              🚀 System Ready!                          ║
echo ╠════════════════════════════════════════════════════════╣
echo ║  Backend:  http://localhost:%BACKEND_PORT%                     ║
echo ║  Frontend: http://localhost:%FRONTEND_PORT%                     ║
echo ║  API Docs: http://localhost:%BACKEND_PORT%/docs                ║
echo ╚════════════════════════════════════════════════════════╝
echo.

timeout /t 3 >nul
start http://localhost:%FRONTEND_PORT%

echo Press any key to exit (servers will keep running)...
pause >nul