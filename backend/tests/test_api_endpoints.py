"""
Integration tests for FastAPI REST Endpoints
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_records" in data

def test_districts_endpoint():
    response = client.get("/api/districts")
    assert response.status_code == 200
    districts = response.json()
    assert len(districts) == 5
    assert any(d["name"] == "Pune" for d in districts)

def test_syndromes_endpoint():
    response = client.get("/api/syndromes")
    assert response.status_code == 200
    syndromes = response.json()
    assert len(syndromes) == 4

def test_trends_endpoint():
    response = client.get("/api/trends?district_name=Pune&syndrome_id=SYN-ADD")
    assert response.status_code == 200
    data = response.json()
    assert data["district_name"] == "Pune"
    assert "analysis" in data
    assert "series" in data
    assert len(data["series"]) > 0

def test_anomalies_endpoint():
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert "total_active_anomalies" in data
    assert "anomalies" in data

def test_map_hotspots_endpoint():
    response = client.get("/api/map/hotspots")
    assert response.status_code == 200
    hotspots = response.json()
    assert len(hotspots) == 5

def test_simulation_injection():
    payload = {
        "district_name": "Nashik",
        "syndrome_id": "SYN-VBD",
        "spike_percentage": 250,
        "days_duration": 3
    }
    response = client.post("/api/simulate/inject", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OUTBREAK_INJECTED"

def test_export_fhir_endpoint():
    response = client.get("/api/export/fhir?district_name=Pune&syndrome_id=SYN-ADD")
    assert response.status_code == 200
    data = response.json()
    assert data["resourceType"] == "Bundle"
    assert data["type"] == "collection"
    assert len(data["entry"]) > 0
    first_obs = data["entry"][0]["resource"]
    assert first_obs["resourceType"] == "Observation"

def test_export_geojson_endpoint():
    response = client.get("/api/export/geojson")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 5
    assert data["features"][0]["geometry"]["type"] == "Point"

def test_alert_dispatch_endpoint():
    response = client.post("/api/alerts/dispatch?district_name=Pune&syndrome_id=SYN-ADD")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DISPATCHED"
    assert "dispatch_id" in data
    assert len(data["action_protocol"]) > 0

def test_alert_history_endpoint():
    response = client.get("/api/alerts/history")
    assert response.status_code == 200
    data = response.json()
    assert "total_dispatched" in data
    assert data["total_dispatched"] >= 1


