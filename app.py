import os
import json
import joblib
import pandas as pd
import numpy as np
import logging

from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader

from src.feature_engineering import add_features
from src.pydantic_validaton import InputData, RecommendInput


# ============================================================
# CONFIGURATION DU LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agri-api")


# ============================================================
# CONFIGURATION DE LA SÉCURITÉ

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.error("La variable d'environnement API_KEY n'est pas définie !")
    raise RuntimeError("API_KEY manquante dans les variables d'environnement")

api_key_header = APIKeyHeader(name="x-api-key")


def _verify_api_key(x_api_key: str = Security(api_key_header)):
    """Sécurité pour l'endpoint predict"""
    if x_api_key != API_KEY:
        logger.warning("Tentative d'accès avec une API key invalide")
        raise HTTPException(status_code=401, detail="Invalid API key")


# ============================================================
# CHARGEMENT DU MODÈLE ET DES ARTEFACTS

try:
    logger.info("Chargement du modèle et des artefacts...")

    model = joblib.load("model_artifacts/final_model.pkl")
    country_to_cluster = joblib.load("model_artifacts/country_to_cluster.pkl")

    with open("model_artifacts/metadata.json", "r") as f:
        metadata = json.load(f)

    with open("model_artifacts/cat_info.json", "r") as f:
        cat_data = json.load(f)
        ITEMS = cat_data["Items"]
        AREAS = cat_data["Areas"]

    logger.info("Modèle et artefacts chargés avec succès.")

except Exception as e:
    logger.error(f"Erreur lors du chargement des artefacts : {e}")
    raise RuntimeError(f"Erreur lors du chargement des artefacts : {e}")


# ============================================================
# INITIALISATION DE L'API

app = FastAPI(
    title="Agriculture Yield Prediction API",
    description="API de prédiction du rendement agricole basée sur un modèle ML",
    version="1.0.0"
)
# Expose les dépendances globales pour les tests 
app.model = model 
app.ITEMS = ITEMS
app.AREAS = AREAS

#==============================================================
# Fontion de utilitaires 
# preparation des données
def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    # Transformation log1p
    df["pesticides_tonnes_log"] = np.log1p(df["pesticides_tonnes"])
    df.drop(columns=["pesticides_tonnes"], inplace=True)
    logger.info("Transformation log1p appliquée.")

    # Ajout du cluster climatique
    df["climate_cluster"] = df["Area"].map(country_to_cluster)
    if df["climate_cluster"].isna().any():
        logger.warning(f"Pays inconnu : {df['Area'].iloc[0]}")
        raise ValueError(f"Pays inconnu : {df['Area'].iloc[0]}")

    # Feature engineering
    df = add_features(df)
    logger.info("Feature engineering terminé.")

    return df

# prediction
def predict_single(df: pd.DataFrame) -> float:
    df_prepared = prepare_features(df)
    pred_log = app.model.predict(df_prepared)[0]

    pred = float(np.expm1(pred_log))
    logger.info(f"Prédiction effectuée : {pred}")
    return pred


# ============================================================
# ENDPOINTS

@app.get("/")
async def home():
    logger.info("Endpoint / appelé")
    return {"message": "Bienvenue sur l'API de prédiction agricole"}


@app.get("/config")
async def get_config():
    """Retourne les listes de pays et de cultures pour le frontend"""
    logger.info("Endpoint /config appelé")
    return {
        "items": ITEMS,
        "areas": AREAS,
        "metadata": metadata
    }


@app.get("/model_info")
async def model_info():
    logger.info("Endpoint /model_info appelé")
    return metadata



@app.post("/predict")
async def predict_agro(data: InputData, _: str = Security(_verify_api_key)):
    try:
        logger.info(f"Requête reçue : {data.model_dump()}")
        # Conversion en DataFrame
        df = pd.DataFrame([data.model_dump()])
        logger.info("Conversion en DataFrame effectuée.")
        pred = predict_single(df)
        return {"prediction (hg/ha)": pred}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except KeyError as ke:
        raise HTTPException(status_code=422, detail=f"Colonne manquante : {ke}")

    except Exception:
        raise HTTPException(status_code=500, detail="Erreur interne")


#---------------------------------------------------------------------
@app.post('/recommend')
async def recommandation(data: RecommendInput, _:str = Security(_verify_api_key)):
    try:
        logger.info(f"Requête reçue : {data.model_dump()}")
        results = {}
        for item in app.ITEMS:
            row = data.model_dump()
            # injectons la culture
            row['Item'] = item
            df = pd.DataFrame([row])

            pred = predict_single(df)
            results[item] = pred
        
        return {"recommendations": results}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except KeyError as ke:
        raise HTTPException(status_code=422, detail=f"Colonne manquante : {ke}")
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur interne")


# ============================================================
# LANCEMENT LOCAL

if __name__ == "__main__":
    import uvicorn
    logger.info("Démarrage du serveur Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
