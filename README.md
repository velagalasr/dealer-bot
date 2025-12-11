---
title: Dealer Bot
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: latest
app_file: app.py
pinned: false
---

# 🤖 Dealer Bot

A production-ready RAG-based Q&A system for dealer support using intelligent multi-agent orchestration.

## Features

- **4 Intelligent Agents:**
  - Intent Classifier Agent (Rules + LLM hybrid)
  - Anomaly Detection Agent (Security & fraud detection)
  - RAG Agent (Intelligent document retrieval & ranking)
  - Response Synthesis Agent (Context-aware responses)

- **Semantic Search:** Vector database with embeddings
- **Document Management:** Upload and manage knowledge base
- **Security:** Malicious query detection, risk scoring
- **Web UI:** Gradio interface for easy interaction

## Quick Start (Local)

### Prerequisites
- Python 3.11 (compatible - Python 3.14 not supported yet)
- OpenAI API Key

### Setup
```bash
# Clone repo
git clone https://github.com/velagalasr/dealer-bot.git
cd dealer-bot

# Create venv with Python 3.11
python -m venv venv

# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set API key in .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

### Start Servers

**Windows - Quick Start (Easiest)**

Just double-click `start.bat` or run:
```cmd
start.bat
```

To stop servers:
```cmd
stop.bat
```

**Alternative Options**

Option 1 - PowerShell script:
```powershell
.\start.ps1
```

Option 2 - Manual (two terminals):
```powershell
# Terminal 1 - FastAPI
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000

# Terminal 2 - Gradio UI
& ".\venv\Scripts\python.exe" app/ui/gradio_app.py
```

**⚠️ Important:** Always use virtual environment Python (`venv\Scripts\python.exe`), not system Python 3.14.

### Access

- **Gradio Chat UI:** http://localhost:7860
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Stop Servers

Windows:
```cmd
stop.bat
```

Or manually:
```powershell
Get-Process python | Stop-Process -Force
```

## Architecture
```
Query
  ↓
Agent 1: Intent Classification (Rules + LLM)
  ↓
Agent 2: Anomaly Detection (Risk scoring + Document search)
  ↓
Agent 3: RAG Retrieval (Smart search + Re-ranking)
  ↓
Agent 4: Response Synthesis (Context-aware generation)
  ↓
Response
```

## Technologies

- **Framework:** FastAPI, Uvicorn, Gradio
- **LLM:** OpenAI GPT
- **Embeddings:** Sentence Transformers
- **Vector DB:** Chroma
- **Document:** PyPDF

## Project Structure
```
dealer-bot/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── llm/                 # LLM agents
│   ├── core/                # RAG system
│   ├── security/            # Security agents
│   ├── agents/              # Orchestrator
│   ├── api/                 # API endpoints
│   └── ui/                  # Gradio UI
├── requirements.txt         # Dependencies
└── README.md
```

## License

MIT

## Author

Built with ❤️ for intelligent dealer support