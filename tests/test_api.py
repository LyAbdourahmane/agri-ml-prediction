import pytest
from app import app


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API de prédiction agricole"}


def test_model_info(client):
    response = client.get("/model_info")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_config(client):
    """Test du nouvel endpoint /config"""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "areas" in data
    assert "metadata" in data


def test_predict_unauthorized(client):
    response = client.post("/predict", json={})
    assert response.status_code == 401


def test_predict_invalid_key(client):
    response = client.post(
        "/predict",
        json={},
        headers={"x-api-key": "wrong_key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"


def test_predict_valid(client):
    payload = {
        "Area": "France",
        "Item": "Maize",
        "Year": 2021,
        "average_rain_fall_mm_per_year": 1000.0,
        "avg_temp": 20.0,
        "pesticides_tonnes": 50.0
    }

    headers = {"x-api-key": "test_key_123"}

    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 200
    assert "prediction (hg/ha)" in response.json()
    assert isinstance(response.json()["prediction (hg/ha)"], float)


def test_predict_invalid_payload(client):
    payload = {
        "Area": "France",
        "Item": "Maize",
        "Year": 1800  # invalide
    }
    headers = {"x-api-key": "test_key_123"}

    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 422


def test_recommend(client):
    payload = {
        "Area": "France",
        "Year": 2021,
        "average_rain_fall_mm_per_year": 1000.0,
        "avg_temp": 20.0,
        "pesticides_tonnes": 50.0
    }

    headers = {"x-api-key": "test_key_123"}

    response = client.post("/recommend", json=payload, headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], dict)

    # Vérifie que chaque prédiction est un float
    for value in data["recommendations"].values():
        assert isinstance(value, float)
