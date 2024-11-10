import pytest
from fastapi import status
from httpx import AsyncClient
import io

@pytest.mark.asyncio
async def test_create_document(client, db_session):
    """Test document creation."""
    # First create a company
    company_response = client.post("/api/v1/companies/", json={
        "name": "Test Company",
        "business_number": "123-45-67890"
    })
    company_id = company_response.json()["id"]

    # Create a test file
    file_content = b"Test document content"
    files = {
        "file": ("test.txt", io.BytesIO(file_content), "text/plain")
    }
    form_data = {
        "company_id": str(company_id),
        "document_type": "business_plan"
    }

    response = client.post(
        "/api/v1/documents/upload",
        files=files,
        data=form_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["company_id"] == company_id
    assert len(data["sections"]) > 0

@pytest.mark.asyncio
async def test_get_document(client):
    """Test getting a document."""
    # Create test data first
    company_response = client.post("/api/v1/companies/", json={
        "name": "Test Company",
        "business_number": "123-45-67890"
    })
    company_id = company_response.json()["id"]

    document_data = {
        "title": "Test Document",
        "type": "business_plan",
        "company_id": company_id
    }
    create_response = client.post("/api/v1/documents/", json=document_data)
    document_id = create_response.json()["id"]

    # Then get the document
    response = client.get(f"/api/v1/documents/{document_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == document_id
    assert data["title"] == document_data["title"]
