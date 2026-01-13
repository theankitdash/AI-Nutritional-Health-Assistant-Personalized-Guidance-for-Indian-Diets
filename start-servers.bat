@echo off
echo ========================================
echo Starting Nutrify-Health Application
echo ========================================
echo.
echo Starting FastAPI Backend on port 8000...
echo.

start cmd /k "cd /d %~dp0 && uvicorn app.main:app --reload"

timeout /t 3 /nobreak > nul

echo Starting Next.js Frontend on port 3000...
echo.

start cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo FastAPI Backend: http://localhost:8000
echo Next.js Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
echo ========================================
pause > nul
