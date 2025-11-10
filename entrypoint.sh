#!/bin/bash

# Start FastAPI in background
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Gradio in foreground
python app/ui/gradio_app.py