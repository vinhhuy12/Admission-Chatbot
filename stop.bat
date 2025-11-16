@echo off
REM ============================================
REM Admissions Counseling Chatbot - Stop Script
REM ============================================

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     ADMISSIONS COUNSELING CHATBOT - STOPPING SERVICES         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo 🛑 Stopping backend server (Python)...
taskkill /FI "WINDOWTITLE eq Backend Server*" /F >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend server stopped
) else (
    echo ⚠️  Backend server not found or already stopped
)

echo.
echo 🛑 Stopping frontend server (Node.js)...
taskkill /FI "WINDOWTITLE eq Frontend Server*" /F >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Frontend server stopped
) else (
    echo ⚠️  Frontend server not found or already stopped
)

echo.
echo 🛑 Killing any remaining Python processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>nul
)

echo.
echo 🛑 Killing any remaining Node processes on port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>nul
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ ALL SERVICES STOPPED                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

pause

