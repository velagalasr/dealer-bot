# Quick Start Guide

## Get Running in 5 Minutes

### Step 1: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment
```bash
copy .env.example .env

# Edit .env and add your OpenAI API Key
# OPENAI_API_KEY=sk-your-key-here
```

### Step 4: Run Server
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Step 5: Test API
Open browser: http://localhost:8000/docs

---

## Project Structure
```
dealer-bot/
├── app/                    # Main application code
│   ├── main.py            # FastAPI app
│   ├── config.py          # Settings
│   ├── auth.py            # Authentication
│   ├── api/               # API endpoints
│   ├── core/              # RAG system (embeddings, DB, retrieval)
│   ├── llm/               # LLM interactions
│   ├── agents/            # Multi-agent orchestration
│   └── utils/             # Utilities (logging, caching)
├── data/                  # Local data storage
│   ├── documents/         # Downloaded documents
│   └── vectors/           # Vector database
├── tests/                 # Test files
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker config
└── README.md             # Full documentation
```

## Current Status (Phase 1: Foundation)

✅ **Completed:**
- Project structure
- FastAPI setup with endpoints
- Authentication system
- Configuration management
- Logging setup
- Vector DB initialization
- Document loader skeleton
- All placeholder modules

⏳ **Next Phase (Phase 2: RAG Core):**
- Download documents
- Extract text from PDFs
- Generate embeddings
- Populate vector database
- Implement semantic search

---

## Quick Testing

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Query (with API key)
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "X-API-Key: default-dev-key" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Help me\"}"
```

### Test 3: Using Swagger UI
Visit: http://localhost:8000/docs
- Click "Authorize" (top right)
- Enter API Key: `default-dev-key`
- Try endpoints interactively

---

## Environment Variables

Create `.env` file with:
```
OPENAI_API_KEY=your-key-here
API_KEY=default-dev-key
DEBUG=True
ENVIRONMENT=development
```

---

## Troubleshooting

### Port 8000 already in use
```bash
python -m uvicorn app.main:app --port 8001
```

### Module not found error
```bash
# Make sure venv is activated, then reinstall
pip install -r requirements.txt
```

### OpenAI API Key error
- Check `.env` file has your key
- Make sure no extra spaces

### Vector DB issues
```bash
mkdir -p data\documents data\vectors
```

---

## Next Steps

1. ✅ You now have Phase 1 complete!
2. Run server locally with `python -m uvicorn app.main:app --reload`
3. Test endpoints in Swagger UI
4. Phase 2 next: Document processing and embeddings

---

## Support

- Check README.md for full documentation
- API docs available at http://localhost:8000/docs
- Phase-by-phase implementation guide in README.md
```

4. **Save the file** with `Ctrl+S`

---

## 🤔 **What's in this file?**

- **Quick setup** - Fastest way to get running
- **5 main steps** - Copy, paste, done
- **File structure** - Quick reference
- **Testing examples** - 3 ways to test
- **Common problems** - Quick fixes
- **No details** - Just the essentials

---

## ✅ **CHECK YOUR WORK**

You should now see:
```
dealer-bot/
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── QUICKSTART.md  ← Should be here!