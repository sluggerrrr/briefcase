"""
Tests for Document API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from tests.conftest import TestingSessionLocal, override_get_db

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestDocumentAPI:
    """Test document API endpoints."""
    
    def test_list_documents_requires_auth(self):
        """Test that listing documents requires authentication."""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 403
    
    def test_list_documents_with_auth(self, auth_headers):
        """Test listing documents with authentication."""
        response = client.get("/api/v1/documents/", headers=auth_headers)
        # Should return 200 with empty list for new user
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_documents_with_query_params(self, auth_headers):
        """Test listing documents with query parameters."""
        response = client.get(
            "/api/v1/documents/?sent=true&received=false", 
            headers=auth_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_document_not_found(self, auth_headers):
        """Test getting a non-existent document."""
        response = client.get("/api/v1/documents/nonexistent", headers=auth_headers)
        assert response.status_code == 404
    
    def test_upload_document_requires_auth(self):
        """Test that uploading documents requires authentication."""
        document_data = {
            "title": "Test Document",
            "file_name": "test.txt",
            "mime_type": "text/plain",
            "content": "dGVzdCBjb250ZW50",  # base64 encoded "test content"
            "recipient_id": "test-recipient-id"
        }
        response = client.post("/api/v1/documents/", json=document_data)
        assert response.status_code == 403


class TestDocumentRouteRegistration:
    """Test that document routes are properly registered."""
    
    def test_document_routes_exist(self):
        """Test that document routes exist in the app."""
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        # Check main document routes
        assert "/api/v1/documents/" in routes
        assert "/api/v1/documents/{document_id}" in routes
        assert "/api/v1/documents/{document_id}/download" in routes
        assert "/api/v1/documents/{document_id}/content" in routes
    
    def test_app_startup(self):
        """Test that the FastAPI app starts up correctly."""
        assert app.title == "Briefcase API"
        assert app.version == "1.0.0"
    
    def test_health_endpoint(self):
        """Test the health endpoint works."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "briefcase-api"


class TestDocumentAPIMethods:
    """Test HTTP methods on document endpoints."""
    
    def test_documents_get_method(self):
        """Test GET method on documents endpoint."""
        response = client.get("/api/v1/documents/")
        # Should return 403 (forbidden) when no auth token provided
        assert response.status_code == 403
    
    def test_documents_post_method(self):
        """Test POST method on documents endpoint."""
        document_data = {
            "title": "Test Document",
            "file_name": "test.txt",
            "mime_type": "text/plain",
            "content": "dGVzdA==",
            "recipient_id": "test-id"
        }
        response = client.post("/api/v1/documents/", json=document_data)
        # Should return 403 (forbidden) when no auth token provided
        assert response.status_code == 403
    
    def test_document_detail_methods(self):
        """Test methods on document detail endpoint."""
        # GET method
        response = client.get("/api/v1/documents/test-id")
        assert response.status_code == 403  # Should require auth
        
        # PUT method  
        response = client.put("/api/v1/documents/test-id", json={"title": "Updated"})
        assert response.status_code == 403  # Should require auth
        
        # DELETE method
        response = client.delete("/api/v1/documents/test-id")
        assert response.status_code == 403  # Should require auth