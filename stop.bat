@echo off
echo Stopping Dealer Bot servers...
taskkill /F /IM python.exe /T >nul 2>&1
echo All Python processes stopped.
pause
