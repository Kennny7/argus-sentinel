import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir / "services" / "gateway-api" / "src"))

from main import app

client = TestClient(app)

def test_gateway_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["system"] == "ARGUS SENTINEL"
    assert data["status"] == "OPERATIONAL"

def test_gateway_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_list_incidents():
    response = client.get("/api/v1/incidents?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "records" in data
    assert len(data["records"]) <= 10

def test_surveillance_cameras():
    response = client.get("/api/v1/surveillance/cameras")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5

def test_active_targets():
    response = client.get("/api/v1/surveillance/targets/active")
    assert response.status_code == 200
    data = response.json()
    assert "active_targets" in data
    assert len(data["active_targets"]) > 0

def test_streams_status():
    response = client.get("/api/v1/streams/status")
    assert response.status_code == 200
    data = response.json()
    assert "connectors" in data
