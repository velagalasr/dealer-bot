"""
Test suite for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Initialize test client
client = TestClient(app)

# Test API Key
TEST_API_KEY = "default-dev-key"


class TestHealth:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRoot:
    """Test root endpoint"""
    
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "Dealer Bot"
        assert "endpoints" in data


class TestQueryEndpoint:
    """Test query endpoint"""
    
    def test_query_without_auth(self):
        """Test query endpoint without auth should fail"""
        response = client.post(
            "/api/v1/query",
            json={"query": "Test query"}
        )
        assert response.status_code == 403
    
    def test_query_with_valid_auth(self):
        """Test query endpoint with valid auth"""
        response = client.post(
            "/api/v1/query",
            json={"query": "What is maintenance?"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
    
    def test_query_with_invalid_auth(self):
        """Test query endpoint with invalid auth"""
        response = client.post(
            "/api/v1/query",
            json={"query": "Test"},
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 403


class TestIntentEndpoint:
    """Test intent classification endpoint"""
    
    def test_intent_without_auth(self):
        """Test intent endpoint without auth should fail"""
        response = client.post(
            "/api/v1/intent",
            json={"text": "My equipment is broken"}
        )
        assert response.status_code == 403
    
    def test_intent_with_valid_auth(self):
        """Test intent endpoint with valid auth"""
        response = client.post(
            "/api/v1/intent",
            json={"text": "How do I fix this?"},
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "confidence" in data


class TestDocumentUpload:
    """Test document upload endpoint"""
    
    def test_upload_without_auth(self):
        """Test upload without auth should fail"""
        response = client.post(
            "/api/v1/documents/upload",
            json={"url": "https://example.com/doc.pdf"}
        )
        assert response.status_code == 403
    
    def test_upload_with_valid_auth(self):
        """Test upload with valid auth"""
        response = client.post(
            "/api/v1/documents/upload",
            json={
                "url": "https://example.com/document.pdf",
                "document_type": "manual"
            },
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert "status" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])