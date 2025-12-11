"""Test query endpoint"""
import requests
import json

url = "http://localhost:8000/api/v1/query"
headers = {"X-API-Key": "default-dev-key"}
data = {
    "query": "What is dealer support?",
    "session_id": "test-123",
    "user_id": "gradio-user"
}

print("Sending query...")
response = requests.post(url, json=data, headers=headers, timeout=30)

print(f"\nStatus: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"\nResponse: {result.get('response', 'No response')[:300]}...")
    print(f"\nIntent: {result.get('intent')}")
    print(f"Documents retrieved: {result.get('retrieval_info', {}).get('documents_retrieved', 0)}")
    print(f"Retrieval confidence: {result.get('retrieval_info', {}).get('retrieval_confidence', 0)}")
else:
    print(f"Error: {response.text}")
