import pytest
import pandas as pd
import numpy as np
from src.feature_engineering import add_features

def test_add_features_logic():
    """Test que les features sont bien calculées"""
    # Données d'entrée simulées
    data = {
        "pesticides_tonnes_log": [np.log1p(100)], # ~4.615
        "average_rain_fall_mm_per_year": [1000.0],
        "avg_temp": [25.0]
    }
    df = pd.DataFrame(data)
    
    # Appel de la fonction
    df_res = add_features(df)
    
    # Vérifications
    # 1. water_stress = rain / temp = 1000 / 25 = 40
    assert "water_stress" in df_res.columns
    assert df_res["water_stress"].iloc[0] == pytest.approx(40.0)
    
    # 2. rain_temp_interaction = rain * temp = 1000 * 25 = 25000
    assert "rain_temp_interaction" in df_res.columns
    assert df_res["rain_temp_interaction"].iloc[0] == pytest.approx(25000.0)
    
    # 3. input_intensity = pest_log / rain = 4.615... / 1000 = ~0.0046
    expected_intensity = data["pesticides_tonnes_log"][0] / 1000.0
    assert df_res["input_intensity"].iloc[0] == pytest.approx(expected_intensity)
    
    # 4. pest_temp_interaction = pest_log * temp
    expected_pest_temp = data["pesticides_tonnes_log"][0] * 25.0
    assert "pest_temp_interaction" in df_res.columns
    assert df_res["pest_temp_interaction"].iloc[0] == pytest.approx(expected_pest_temp)

def test_add_features_empty():
    """Test avec un dataframe vide"""
    df = pd.DataFrame(columns=["pesticides_tonnes_log", "average_rain_fall_mm_per_year", "avg_temp"])
    df_res = add_features(df)
    assert df_res.empty
    assert "water_stress" in df_res.columns
