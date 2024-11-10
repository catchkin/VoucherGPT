import pytest
from fastapi import status
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_section(client, db_session):
    """Test section creation."""
    # Create prerequisite data
    company_response = client.post("/api/v1/companies/", json={
        "name": "Test Company",
        "business_number": "123-45-67890"
    })
    company_id = company_response.json()["id"]

    document_response = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "type": "business_plan",
        "company_id": company_id
    })
    document_id = document_response.json()["id"]

    # Create section
    section_data = {
        "type": "executive_summary",
        "title": "Test Section",
        "content": "Test content",
        "document_id": document_id,
        "company_id": company_id
    }
    response = client.post("/api/v1/sections/", json=section_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == section_data["title"]
    assert data["type"] == section_data["type"]

@pytest.mark.asyncio
async def test_reorder_sections(client):
    """Test reordering sections."""
    # Create prerequisite data first
    company_id = client.post("/api/v1/companies/", json={
        "name": "Test Company",
        "business_number": "123-45-67890"
    }).json()["id"]

    document_id = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "type": "business_plan",
        "company_id": company_id
    }).json()["id"]

    # Create multiple sections
    sections = []
    for i in range(3):
        section_response = client.post("/api/v1/sections/", json={
            "type": "executive_summary",
            "title": f"Test Section {i}",
            "content": f"Test content {i}",
            "document_id": document_id,
            "company_id": company_id
        })
        sections.append(section_response.json())

    # Reorder sections
    reorder_data = {
        str(sections[0]["id"]): 2,
        str(sections[1]["id"]): 0,
        str(sections[2]["id"]): 1
    }
    response = client.put(f"/api/v1/sections/document/{document_id}/reorder", json=reorder_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert data[0]["id"] == sections[1]["id"]
    assert data[1]["id"] == sections[2]["id"]
    assert data[2]["id"] == sections[0]["id"]
