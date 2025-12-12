#!/usr/bin/env python3
"""Export vector DB chunks to JSON for deployment"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.vector_db import vector_db
import json

# Get all documents with metadata and embeddings
collection = vector_db.collection
results = collection.get(include=["documents", "metadatas", "embeddings"])

data = {
    "documents": results["documents"],
    "metadatas": results["metadatas"],
    "embeddings": results["embeddings"],
    "ids": results["ids"]
}

# Save to JSON
output_file = Path("data/documents/chunks.json")
output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"✅ Exported {len(data['documents'])} chunks to {output_file}")
print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
