# Dealer Solutions Bot

A RAG-based Q&A system for equipment and services, built with FastAPI, OpenAI, and Chroma.

## Architecture Overview
```
User Query
    ↓
API Gateway (FastAPI + Auth)
    ↓
Intent Classifier (LLM) → Routes to Specialist
    ↓
Document Retriever (Semantic Search) → Chroma Vector DB
    ↓
Response Synthesizer (LLM) → OpenAI GPT
    ↓
Response + Sources
```

## Prerequisites

- Python 3.10+
- OpenAI API Key
- Git

## Local Setup

### 1. Clone and Navigate
```bash
# Create project directory
mkdir dealer-bot
cd dealer-bot
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy example to .env
copy .env.example .env

# Edit .env with your values
# Important: Add your OpenAI API Key
```

### 5. Run FastAPI Server Locally
```bash
python -m uvicorn app.main:app --reload --port 8000
```

Access the API at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs` (Swagger UI)
- Alternative Docs: `http://localhost:8000/redoc` (ReDoc)

## Project Structure
```
dealer-bot/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── auth.py                 # API key auth
│   ├── api/
│   │   ├── routes.py           # API endpoints
│   │   └── models.py           # Pydantic models
│   ├── core/
│   │   ├── document_loader.py  # Document handling
│   │   ├── vector_db.py        # Chroma DB
│   │   ├── embeddings.py       # OpenAI embeddings
│   │   └── retriever.py        # Semantic search
│   ├── llm/
│   │   ├── openai_client.py    # OpenAI wrapper
│   │   ├── intent_classifier.py
│   │   └── response_synthesizer.py
│   ├── agents/
│   │   ├── orchestrator.py     # Agent coordination
│   │   ├── router.py           # Query routing
│   │   └── specialists.py      # Specialist agents
│   └── utils/
│       ├── logger.py
│       └── cache.py
├── tests/
│   └── test_api.py
├── data/
│   ├── documents/              # Downloaded PDFs
│   └── vectors/                # Chroma DB
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Query Processing
```bash
POST /api/v1/query
Header: X-API-Key: your_api_key
Content-Type: application/json

{
  "query": "How do I maintain my equipment?",
  "session_id": "optional-session-id"
}
```

### Intent Classification
```bash
POST /api/v1/intent
Header: X-API-Key: your_api_key
Content-Type: application/json

{
  "text": "My equipment is making strange noises"
}
```

### Upload Document
```bash
POST /api/v1/documents/upload
Header: X-API-Key: your_api_key
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "document_type": "manual"
}
```

## Testing API Locally

### Using Swagger UI (Easiest)
1. Go to: `http://localhost:8000/docs`
2. Click "Authorize" and enter your API key
3. Try endpoints interactively

### Using cURL
```bash
# Test health check
curl http://localhost:8000/health

# Test query with API key
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "X-API-Key: default-dev-key" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is Caterpillar?\"}"
```

### Using Python
```python
import requests

headers = {"X-API-Key": "default-dev-key"}

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={"query": "Help with maintenance"},
    headers=headers
)

print(response.json())
```

## Phase-by-Phase Development

### ✅ Phase 1: Foundation (COMPLETED)
- [x] Project structure
- [x] FastAPI setup
- [x] Configuration management
- [x] API key authentication
- [x] Placeholder endpoints

### ⏳ Phase 2: Core RAG System (NEXT)
- [ ] Document downloading from website
- [ ] PDF text extraction
- [ ] Text chunking
- [ ] OpenAI embeddings generation
- [ ] Chroma vector DB population
- [ ] Semantic search implementation

### ⏳ Phase 3: Bot Intelligence
- [ ] Intent classifier refinement
- [ ] Multi-agent orchestration
- [ ] Specialist agent implementation
- [ ] Response synthesis
- [ ] Caching optimization

### ⏳ Phase 4: UI & Testing
- [ ] Streamlit/Gradio UI
- [ ] Unit tests
- [ ] Integration tests
- [ ] Error handling

### ⏳ Phase 5: Deployment
- [ ] Docker containerization
- [ ] HuggingFace Spaces deployment
- [ ] Environment setup
- [ ] Monitoring

## Common Issues

### OpenAI API Key Error
```
Error: OPENAI_API_KEY environment variable is not set
```
**Solution**: Make sure your `.env` file has `OPENAI_API_KEY=your_key_here`

### Vector DB Connection Error
```
Error: Failed to initialize vector database
```
**Solution**: Check that `data/vectors/` directory has write permissions

### Port Already in Use
```
Error: Address already in use (port 8000)
```
**Solution**: Use different port: `python -m uvicorn app.main:app --port 8001`

## Next Steps

1. Download Caterpillar Documents - Phase 2 will implement this
2. Process Documents - Extract text, chunk, and embed
3. Populate Vector DB - Store embeddings in Chroma
4. Test Queries - Verify semantic search works
5. Deploy to HF Spaces - Share your bot

## Support

For issues or questions, refer to:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [Chroma Documentation](https://docs.trychroma.com/)

## License

MIT License
```

4. **Save the file** with `Ctrl+S`

---

## 🤔 **What's in this file?**

- **Title & Description** - What the project is
- **Architecture diagram** - How it works
- **Installation steps** - How to set it up
- **File structure** - Where everything goes
- **API endpoints** - How to use the API
- **Testing examples** - How to test it
- **Phase overview** - What we're building next
- **Troubleshooting** - Common problems and solutions

---

## ✅ **CHECK YOUR WORK**

You should now see:
```
dealer-bot/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md  ← Should be here!