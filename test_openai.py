"""Test OpenAI connection"""
import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key set: {bool(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'MISSING'}...")

try:
    client = OpenAI(api_key=api_key)
    response = client.models.list()
    print(f"✅ OpenAI connection works!")
    print(f"Available models: {len(response.data)}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")