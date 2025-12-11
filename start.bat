@echo off
echo ========================================
echo Starting Dealer Bot Servers
echo ========================================
echo.

cd /d "c:\Gen AI\dealer-bot"

echo [1/2] Starting FastAPI server...
start "FastAPI Server" /B "C:\Gen AI\dealer-bot\venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000

echo Waiting 5 seconds for FastAPI to start...
timeout /t 5 /nobreak > nul

echo [2/2] Starting Gradio UI...
start "Gradio UI" /B "C:\Gen AI\dealer-bot\venv\Scripts\python.exe" app\ui\gradio_app.py

echo Waiting 5 seconds for Gradio to start...
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo Dealer Bot Started!
echo ========================================
echo.
echo Access:
echo   FastAPI: http://localhost:8000/docs
echo   Gradio:  http://localhost:7860
echo.
echo To stop: Run stop.bat or press Ctrl+C
echo.
pause
