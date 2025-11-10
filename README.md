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
```bash
# Clone repo
git clone https://github.com/velagalasr/dealer-bot.git
cd dealer-bot

# Create venv
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key-here"

# Run FastAPI
python -m uvicorn app.main:app --reload --port 8000

# In another terminal, run Gradio
python app/ui/gradio_app.py
```

Access:
- **Gradio UI:** http://localhost:7860
- **API Docs:** http://localhost:8000/docs

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