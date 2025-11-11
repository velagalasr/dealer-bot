#!/bin/bash

echo "=== Starting Dealer Bot Services ==="

# Start FastAPI in background
echo "Starting FastAPI on port 8000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait for FastAPI to be ready
echo "Waiting for FastAPI to start..."
sleep 5

# Check if FastAPI is running
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ FastAPI is ready!"
        break
    fi
    echo "Attempt $i: FastAPI not ready yet, waiting..."
    sleep 1
done

# Start Gradio in foreground
echo "Starting Gradio on port 7860..."
python app/ui/gradio_app.py