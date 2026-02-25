import pytest
from pydantic import ValidationError
from src.pydantic_validaton import InputData, RecommendInput
from unittest.mock import patch

class TestInputData:
    
    @patch("src.pydantic_validaton.get_allowed_items")
    def test_valid_input(self, mock_items):
        """Test nominal avec des données valides"""
        mock_items.return_value = ["Maize", "Wheat"]
        data = {
            "Area": "France",
            "Item": "Maize",
            "Year": 2020,
            "average_rain_fall_mm_per_year": 800.0,
            "avg_temp": 15.5,
            "pesticides_tonnes": 500.0
        }
        model = InputData(**data)
        assert model.Area == "France"
        assert model.Item == "Maize"

    @patch("src.pydantic_validaton.get_allowed_items")
    def test_invalid_item(self, mock_items):
        """Test que un item inconnu lève une erreur"""
        mock_items.return_value = ["Maize", "Wheat"]
        data = {
            "Area": "France",
            "Item": "UnknownCrop", 
            "Year": 2020,
            "average_rain_fall_mm_per_year": 800.0,
            "avg_temp": 15.5,
            "pesticides_tonnes": 500.0
        }
        with pytest.raises(ValidationError) as exc:
            InputData(**data)
        assert "Item doit être dans" in str(exc.value)

    def test_year_range(self):
        """Test des bornes de l'année"""
        base_data = {
            "Area": "France", "Item": "Maize", "average_rain_fall_mm_per_year": 800, 
            "avg_temp": 15, "pesticides_tonnes": 500
        }
        
        # Trop vieux
        with pytest.raises(ValidationError):
            InputData(**base_data, Year=1800)
            
        # Trop futur
        with pytest.raises(ValidationError):
            InputData(**base_data, Year=2100)
            
    def test_negative_values(self):
        """Test que les valeurs négatives sont rejetées"""
        base_data = {
            "Area": "France", "Item": "Maize", "Year": 2020, 
            "avg_temp": 15, "pesticides_tonnes": 500
        }
        with pytest.raises(ValidationError):
            InputData(**base_data, average_rain_fall_mm_per_year=-10)

    def test_strip_whitespace(self):
        """Test que les espaces sont retirés"""
        data = {
            "Area": "  France  ",
            "Item": " Maize ",
            "Year": 2020,
            "average_rain_fall_mm_per_year": 800.0,
            "avg_temp": 15.5,
            "pesticides_tonnes": 500.0
        }
        model = InputData(**data)
        assert model.Area == "France"
        assert model.Item == "Maize"

class TestRecommendInput:
    def test_valid_recommend_input(self):
        data = {
            "Area": "France",
            "Year": 2020,
            "average_rain_fall_mm_per_year": 800.0,
            "avg_temp": 15.5,
            "pesticides_tonnes": 500.0
        }
        model = RecommendInput(**data)
        assert model.Area == "France"
        # RecommendInput n'a pas de champ Item
