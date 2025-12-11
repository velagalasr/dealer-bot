"""Test RAG retrieval directly"""
from app.core.rag_agent import rag_agent

# Test a simple query
result = rag_agent.retrieve_and_rank(
    query="What is dealer support?",
    session_id="test-session",
    n_results=5,
    user_id=None,
    doc_type=None  # Don't filter
)

print(f"Success: {result['success']}")
print(f"Documents retrieved: {result['document_count']}")
print(f"Confidence: {result['confidence']}")
print(f"\nRetrieval stats: {result['retrieval_stats']}")

if result['documents']:
    print(f"\nFirst document:")
    print(f"  Text: {result['documents'][0]['document'][:200]}...")
    print(f"  Similarity: {result['documents'][0]['similarity_score']}")
    print(f"  Metadata: {result['documents'][0]['metadata']}")
