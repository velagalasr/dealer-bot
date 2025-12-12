"""Check ChromaDB collection status"""
from app.core.vector_db import vector_db

info = vector_db.get_collection_info()
print(f"Collection Name: {info['name']}")
print(f"Document Count: {info['document_count']}")
print(f"Metadata: {info['metadata']}")

# Try to get some sample documents
try:
    results = vector_db.collection.peek(limit=5)
    print(f"\nSample IDs: {results.get('ids', [])}")
    print(f"Sample Metadatas: {results.get('metadatas', [])}")
except Exception as e:
    print(f"Error peeking: {e}")
