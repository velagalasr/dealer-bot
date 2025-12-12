# Start Dealer Bot Servers

$projectPath = "c:\Gen AI\dealer-bot"
$pythonExe = "$projectPath\venv\Scripts\python.exe"

Write-Host "Starting Dealer Bot..." -ForegroundColor Green
Write-Host ""

# Check if Python exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Virtual environment not found at:" -ForegroundColor Red
    Write-Host "  $pythonExe" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Change to project directory
Set-Location $projectPath

# Start FastAPI
Write-Host "[1/2] Starting FastAPI server on port 8000..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" -WorkingDirectory $projectPath

# Wait for FastAPI to start
Start-Sleep -Seconds 5

# Check if FastAPI started
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✓ FastAPI server started successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ FastAPI server failed to start" -ForegroundColor Red
    Write-Host "  Check if port 8000 is already in use" -ForegroundColor Yellow
}

# Start Gradio
Write-Host "[2/2] Starting Gradio UI on port 7860..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "app\ui\gradio_app.py" -WorkingDirectory $projectPath

# Wait and check
Start-Sleep -Seconds 5

# Check if Gradio started
try {
    $response = Invoke-WebRequest -Uri "http://localhost:7860" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  ✓ Gradio UI started successfully" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Gradio UI failed to start" -ForegroundColor Red
    Write-Host "  Check if port 7860 is already in use" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dealer Bot is running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor White
Write-Host "  * Gradio Chat UI:  http://localhost:7860" -ForegroundColor Cyan
Write-Host "  * API Docs:        http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  * Health Check:    http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the servers:" -ForegroundColor Yellow
Write-Host '  Get-Process python | Stop-Process -Force' -ForegroundColor White
Write-Host ""
