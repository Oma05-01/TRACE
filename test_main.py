import pytest
from fastapi.testclient import TestClient
from main import app, db_farms

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Clear the in-memory store before each test."""
    db_farms.clear()

def get_valid_payload():
    return {
        "farmer_name": "Esigbone Oma",
        "farmer_id": "NG-1234567890",
        "latitude": 6.5244,
        "longitude": 3.3792,
        "farm_size_hectares": 12.5,
        "commodity": "cocoa",
        "agent_id": "AGT-99",
        "submitted_at": "2026-05-26T10:00:00Z"
    }

def test_successful_registration():
    response = client.post("/api/v1/farms/register", json=get_valid_payload())
    assert response.status_code == 201
    data = response.json()
    assert "farm_id" in data
    assert data["passport_status"] == "PENDING"
    assert data["farmer_name"] == "Esigbone Oma"

def test_duplicate_detection():
    payload = get_valid_payload()
    client.post("/api/v1/farms/register", json=payload)
    # Second submission should trigger 409
    response = client.post("/api/v1/farms/register", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]

def test_invalid_gps_coordinates():
    payload = get_valid_payload()
    payload["latitude"] = 95.0  # Invalid, must be <= 90
    response = client.post("/api/v1/farms/register", json=payload)
    assert response.status_code == 422
    assert "latitude" in response.json()["errors"]

def test_invalid_commodity_type():
    payload = get_valid_payload()
    payload["commodity"] = "rice"  # Not in Enum
    response = client.post("/api/v1/farms/register", json=payload)
    assert response.status_code == 422
    assert "commodity" in response.json()["errors"]

def test_missing_required_fields():
    payload = get_valid_payload()
    del payload["farmer_id"]
    response = client.post("/api/v1/farms/register", json=payload)
    assert response.status_code == 422
    assert "farmer_id" in response.json()["errors"]