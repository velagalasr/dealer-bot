FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model to avoid runtime issues
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy app
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose ports
EXPOSE 7860 8000

# Run entrypoint script
CMD ["./entrypoint.sh"]