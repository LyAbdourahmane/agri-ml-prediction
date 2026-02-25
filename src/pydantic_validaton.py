from pydantic import BaseModel, Field, validator
import json
import os
import functools

@functools.lru_cache()
def get_allowed_items():
    """Charge les items autorisés de manière paresseuse"""
    path = "model_artifacts/cat_info.json"
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            cat_data = json.load(f)
            return cat_data.get('Items', [])
    except Exception:
        return []

class InputData(BaseModel):
    Area: str = Field(..., description="Le pays de production")
    Item: str = Field(..., description="Le type de culture (ex: Maize, Wheat..)")
    Year: int = Field(..., ge=1900, le=2050, description="Année de production")
    average_rain_fall_mm_per_year: float = Field(..., ge=0, description="Pluviométrie annuelle moyenne en mm")
    avg_temp: float = Field(..., description="Température moyenne annuelle en °C")
    pesticides_tonnes: float = Field(..., ge=0, description="Quantité de pesticides en tonnes")

    # si par erreur on passe des espaces avant et après
    @validator("Area", "Item")
    def strip_strings(cls, v):
        return v.strip()

    # ajoutons une validation pour le type de culture
    @validator('Item')
    def validate_item(cls, v):
        allowed = get_allowed_items()
        if allowed and v not in allowed:
            raise ValueError(f"Item doit être dans {allowed}")
        return v


class RecommendInput(BaseModel):
    Area: str = Field(..., description="Le pays de production")
    Year: int = Field(..., ge=1900, le=2050, description="Année de production")
    average_rain_fall_mm_per_year: float = Field(..., ge=0, description="Pluviométrie annuelle moyenne en mm")
    avg_temp: float = Field(..., description="Température moyenne annuelle en °C")
    pesticides_tonnes: float = Field(..., ge=0, description="Quantité de pesticides en tonnes")

    # si par erreur on passe des espaces avant et après
    @validator("Area")
    def strip_strings(cls, v):
        return v.strip()