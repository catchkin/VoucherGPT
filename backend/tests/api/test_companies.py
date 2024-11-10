import pytest
from fastapi import status
from httpx import AsyncClient

from app.crud import company


@pytest.mark.asyncio
async def test_create_company(client):
    """Test company creation."""
    company_data = {
        "name": "Test Company",
        "business_number": "123-45-67890",
        "industry": "Technology",
        "establishment_date": "2024-01-01",
        "employee_count": 50,
        "annual_revenue": 1000000,
        "description": "Test company description"
    }

    response = client.post("/api/v1/companies/", json=company_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == company_data["name"]
    assert data["business_number"] == company_data["business_number"]

@pytest.mark.asyncio
async def test_get_company(client):
    """Test getting a company."""
    # First create a company
    company_data = {
        "name": "Test Company",
        "business_number": "123-45-67890"
    }
    create_response = client.post("/api/v1/companies/", json=company_data)
    company_id = create_response.json()["id"]

    # Then get the company
    response = client.get(f"/api/v1/companies/{company_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == company_id
    assert data["name"] == company_data["name"]
