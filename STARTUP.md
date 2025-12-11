# Dealer Bot - Startup Guide

## What Was The Problem?

### Root Cause
Your system has **Python 3.14** installed globally, but the project dependencies (LangChain, ChromaDB) are only compatible with **Python 3.11**.

### Why It Failed Initially
1. **Python Version Mismatch**: Running `python -m uvicorn` used Python 3.14 (system-wide)
2. **Pydantic Compatibility Issue**: LangChain uses Pydantic v1, which doesn't work with Python 3.14
3. **Doc Type Filter Bug**: The orchestrator was searching for `doc_type="system"` but your uploaded documents were stored as `doc_type="user"`, so RAG retrieved 0 documents

### What Was Fixed
1. ✅ **Use Python 3.11 from virtual environment** instead of system Python 3.14
2. ✅ **Changed doc_type filter** from `"system"` to `None` in `orchestrator.py` to search ALL documents
3. ✅ **Upgraded ChromaDB** to version 1.3.6 for better compatibility

---

## How To Start Servers Next Time

### Prerequisites
- Make sure you're in the project directory: `cd 'c:\Gen AI\dealer-bot'`
- Ensure OpenAI API key is set in environment or `.env` file

### Option 1: Quick Start (Two Terminals)

**Terminal 1 - FastAPI Server:**
```powershell
cd 'c:\Gen AI\dealer-bot'
& "C:/Gen AI/dealer-bot/venv/Scripts/python.exe" -m uvicorn app.main:app --port 8000
```

**Terminal 2 - Gradio UI:**
```powershell
cd 'c:\Gen AI\dealer-bot'
& "C:/Gen AI/dealer-bot/venv/Scripts/python.exe" app/ui/gradio_app.py
```

### Option 2: One-Command Startup (Background Processes)

**PowerShell Script:**
```powershell
cd 'c:\Gen AI\dealer-bot'

# Start FastAPI in background
Start-Process -NoNewWindow -FilePath "C:/Gen AI/dealer-bot/venv/Scripts/python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000"

# Wait 5 seconds for FastAPI to start
Start-Sleep -Seconds 5

# Start Gradio UI in background
Start-Process -NoNewWindow -FilePath "C:/Gen AI/dealer-bot/venv/Scripts/python.exe" -ArgumentList "app/ui/gradio_app.py"

Write-Host "Servers starting..."
Write-Host "FastAPI: http://localhost:8000"
Write-Host "Gradio UI: http://localhost:7860"
```

### Option 3: Create Startup Scripts

**Create `start.ps1` file** in your project root:
```powershell
# Save this as: c:\Gen AI\dealer-bot\start.ps1

$projectPath = "c:\Gen AI\dealer-bot"
$pythonExe = "$projectPath\venv\Scripts\python.exe"

Write-Host "Starting Dealer Bot..." -ForegroundColor Green

# Check if Python exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Start FastAPI
Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8000" -WorkingDirectory $projectPath

# Wait for FastAPI to start
Start-Sleep -Seconds 5

# Start Gradio
Write-Host "Starting Gradio UI..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "app\ui\gradio_app.py" -WorkingDirectory $projectPath

# Wait and check
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ Servers started!" -ForegroundColor Green
Write-Host "  FastAPI: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Gradio:  http://localhost:7860" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop servers, close the terminal or run: Get-Process python | Stop-Process" -ForegroundColor Yellow
```

**Then just double-click or run:**
```cmd
start.bat
```

**Or from command line:**
```powershell
cd 'c:\Gen AI\dealer-bot'
.\start.bat
```

---

## Verify Servers Are Running

**Check FastAPI:**
```powershell
curl http://localhost:8000/health
```

**Check Gradio:**
```powershell
curl http://localhost:7860
```

---

## Stop Servers

**Option 1: Use stop script (Easiest)**
```cmd
stop.bat
```

**Option 2: Stop all Python processes (PowerShell)**
```powershell
Get-Process python | Stop-Process -Force
```

**Option 3: Stop specific ports (PowerShell)**
```powershell
# Find process on port 8000
$pid = (Get-NetTCPConnection -LocalPort 8000).OwningProcess
Stop-Process -Id $pid -Force

# Find process on port 7860
$pid = (Get-NetTCPConnection -LocalPort 7860).OwningProcess
Stop-Process -Id $pid -Force
```

---

## Important Notes

### Why Use Virtual Environment Python?
- ✅ **System Python**: 3.14 (incompatible)
- ✅ **Venv Python**: 3.11 (compatible)
- **Always use**: `"C:/Gen AI/dealer-bot/venv/Scripts/python.exe"`

### ChromaDB Data Persistence
- Your documents are stored in: `c:\Gen AI\dealer-bot\data\vectors\`
- They **persist across restarts** automatically
- Currently: **79 chunks** from "Caterpillar Dealer Service FAQs.pdf"

### No Need To Re-upload Documents
- ChromaDB uses SQLite to persist data
- Once uploaded, documents remain available after server restart
- Only re-upload if you want to add NEW documents

---

## Troubleshooting

### Error: "Port already in use"
```powershell
# Find what's using the port
Get-NetTCPConnection -LocalPort 8000 | Select OwningProcess
# Kill that process
Stop-Process -Id <PID> -Force
```

### Error: "Module not found"
```powershell
# Reinstall dependencies
cd 'c:\Gen AI\dealer-bot'
& "C:/Gen AI/dealer-bot/venv/Scripts/python.exe" -m pip install -r requirements.txt
```

### Error: "OpenAI API key not set"
```powershell
# Set in PowerShell session
$env:OPENAI_API_KEY = "your-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

---

## Access URLs

- **Gradio Chat UI**: http://localhost:7860
- **FastAPI Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Quick Command Reference

| Task | Command |
|------|---------|
| **Start Both** | `start.bat` |
| **Stop Both** | `stop.bat` |
| Start FastAPI | `& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000` |
| Start Gradio | `& ".\venv\Scripts\python.exe" app/ui/gradio_app.py` |
| Check Health | `curl http://localhost:8000/health` |
| Check ChromaDB | `& ".\venv\Scripts\python.exe" check_chroma.py` |

---

**Last Updated**: December 11, 2025
