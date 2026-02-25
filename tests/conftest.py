import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajout du dossier racine au path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# On fixe une clé API pour les tests AVANT d'importer l'app
os.environ["API_KEY"] = "test_key_123"

from app import app


@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)
