import os
import json
import logging
import requests
import gradio as gr
import pandas as pd
import plotly.express as px

from src.pydantic_validaton import InputData, RecommendInput

# --------------------------------------------------------------
# CONFIGURATION LOGGING + API KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("gradio-ui")

CLE_API = os.getenv("API_KEY") 
API_URL = os.getenv("API_URL", "http://localhost:8000")
URL_PREDICT = f"{API_URL}/predict"
URL_RECOMMEND = f"{API_URL}/recommend"


# --------------------------------------------------------------
# RÉCUPÉRATION DE LA CONFIGURATION (DÉCOUPLAGE)

def fetch_config():
    try:
        logger.info(f"Récupération de la configuration sur {API_URL}/config...")
        response = requests.get(f"{API_URL}/config", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erreur lors de la récupération de la config : {response.text}")
    except Exception as e:
        logger.error(f"Impossible de contacter l'API pour la config : {e}")
    
    # Valeurs par défaut si l'API est injoignable
    return {"items": [], "areas": [], "metadata": {}}

config = fetch_config()
ITEMS = config.get("items", [])
AREAS = config.get("areas", [])
metadata = config.get("metadata", {})

# Extraction des métriques
metrics = metadata.get("metrics", {})
mae = metrics.get("MAE", 0)
rmse = metrics.get("RMSE", 0)
r2 = metrics.get('R2', 0)


# --------------------------------------------------------------
# FONCTION DE PRÉDICTION

def prediction(area, item, year, rain, temp, pesticides):
    try:
        data = InputData(
            Area=area,
            Item=item,
            Year=year,
            average_rain_fall_mm_per_year=rain,
            avg_temp=temp,
            pesticides_tonnes=pesticides
        )

        dict_data = data.model_dump()
        logger.info(f"Envoi des données : {dict_data}")

        response = requests.post(
            URL_PREDICT,
            json=dict_data,
            headers={"x-api-key": CLE_API},
            timeout=60
        )
        if response.status_code != 200:
            logger.error(f"Erreur API : {response.text}")
            return f"Erreur API : {response.text}", gr.update(visible=False)

        result = response.json()
        logger.info(f"Réponse API : {result}")
        prediction_value = result['prediction (hg/ha)'] 
        mae_text = f"± {mae:.2f} hg/ha" if mae else "non disponible" 
        output = f""" 
        ## 🌾 Résultat de la prédiction

        Le rendement estimé est de **{prediction_value:.2f} hg/ha** 
        *(hectogrammes par hectare)*

        Incertitude estimée : **{mae_text}** 
        """ 
        return output, gr.update(visible=False)

    except Exception as e:
        logger.error(f"Erreur interne : {e}")
        return f"Erreur interne : {e}", gr.update(visible=False)


def recommendation(area, year, rain, temp, pesticides):
    try:
        data = RecommendInput(
                Area=area,
                Year=year,
                average_rain_fall_mm_per_year=rain,
                avg_temp=temp,
                pesticides_tonnes=pesticides
            )
        dict_data = data.model_dump()
        logger.info(f"Envoi des données : {dict_data}")

        response = requests.post(
            URL_RECOMMEND,
            json=dict_data,
            headers={"x-api-key": CLE_API},
            timeout=60
            )
        if response.status_code != 200:
            logger.error(f"Erreur API : {response.text}")
            return f"Erreur API : {response.text}", None, gr.update(visible=False)

        result = response.json()
        #formatage de l'affichage qu'on veut
        recos = result.get('recommendations', {})

        df = pd.DataFrame({
            'Culture': list(recos.keys()),
            "Rendement (hg/ha)": list(recos.values())
        }).sort_values('Rendement (hg/ha)', ascending=False)

        # graphique
        fig = px.bar(
            df,
            x='Culture',
            y="Rendement (hg/ha)",
            title="Rendement estimé par culture",
            color="Rendement (hg/ha)",
            color_continuous_scale="Viridis"
        )

        # texte 
        best_crop = df.iloc[0]["Culture"] 
        best_value = df.iloc[0]["Rendement (hg/ha)"]
        mae_text = f"± {mae:.2f} hg/ha" if mae else "non disponible" 
        md = f""" 
        ## 🌱 Recommandation des cultures 

        ### Culture recommandée : **{best_crop}** 
        Rendement estimé : **{best_value:.2f} hg/ha**

        Incertitude estimée : **{mae_text}** 
        
        ### Détails complets : 
        """
        
        return md, fig, gr.update(visible=False)       

    except Exception as e:
        logger.error(f"Erreur interne : {e}")
        return f"Erreur interne : {e}", None, gr.update(visible=False)


# créons un loader stylé
def show_loader():
    return gr.update(value="⏳ *Calcul en cours... Merci de patienter.*", visible=True)


# --------------------------------------------------------------
# THÈME
theme = gr.themes.Soft(primary_hue="indigo",secondary_hue="blue",neutral_hue="gray")

# --------------------------------------------------------------
# INTERFACE GRADIO
with gr.Blocks(title="Agriculture Yield Prediction") as interface:

    # ---------------------------------------------------------- 
    # ONGLET 1 : PRÉDICTION
    with gr.Tab("Prédiction"):
        
        # le Header
        with gr.Row():
            gr.Markdown(
                """
                # 🌾 **Prédiction du rendement agricole**  
                ### Interface moderne pour estimer le rendement (hg/ha) selon les conditions climatiques et agricoles.
                """
            )
        gr.Markdown("---")

        # le formulaire
        with gr.Row():
            area_input = gr.Dropdown(AREAS, label="Pays (Area)")
            item_input = gr.Dropdown(ITEMS, label="Culture (Item)")

        with gr.Row():
            year_input = gr.Number(label="Année", value=2026, minimum=1900, maximum=2050)
            rain_input = gr.Number(label="Pluviométrie annuelle (mm)", value=1000.0, minimum=0.0)

        with gr.Row():
            temp_input = gr.Number(label="Température moyenne (°C)", value=20.0)
            pesticides_input = gr.Number(label="Pesticides (tonnes)", value=5.0, minimum=0)

        output_pred = gr.Markdown()
        loader_pred = gr.Markdown(visible=False)
        btn_pred = gr.Button("Prédire le rendement", variant="primary")

        btn_pred.click(fn=show_loader, inputs=None, outputs=loader_pred)
        # après prédiction caché loader
        btn_pred.click(
            fn=prediction,
            inputs=[area_input, item_input, year_input, rain_input, temp_input, pesticides_input],
            outputs=[output_pred, loader_pred]
        )

    # ---------------------------------------------------------- 
    # ONGLET 2 : RECOMMENDATION
    with gr.Tab("Recommendation"):
        
        # le Header
        with gr.Row():
            gr.Markdown("""
            # 🌱 **Recommandation de cultures**
            ### Découvrez quelles cultures offrent le meilleur rendement selon vos conditions.
            """)
        gr.Markdown("---")

        # le formulaire
        with gr.Row():
            area_reco = gr.Dropdown(AREAS, label="Pays (Area)")
            year_reco = gr.Number(label="Année", value=2026, minimum=1900, maximum=2050)

        with gr.Row():
            rain_reco = gr.Number(label="Pluviométrie annuelle (mm)", value=1000.0, minimum=0.0)
            temp_reco = gr.Number(label="Température moyenne (°C)", value=20.0)
        pesticides_reco = gr.Number(label="Pesticides (tonnes)", value=5.0, minimum=0)

        output_reco = gr.Markdown()
        graph_reco = gr.Plot()
        loader_reco = gr.Markdown(visible=False)
        btn_reco = gr.Button("Recommendation", variant="primary")

        btn_reco.click(fn=show_loader, inputs=None, outputs=loader_reco)
        # après prédiction caché loader
        btn_reco.click(
            fn=recommendation,
            inputs=[area_reco, year_reco, rain_reco, temp_reco, pesticides_reco],
            outputs=[output_reco, graph_reco, loader_reco]
        )
    
    # ---------------------------------------------------------- 
    # ONGLET 3 : DÉTAILS DU MODÈLE
    with gr.Tab('Détails du modèle'):
        gr.Markdown(f"""
        # Détails du modèle 
        
        **Modèle utilisé :** `RandomForest` 
        
        ## Performances du modèle

        - **MAE (erreur absolue moyenne)** : `{mae:.2f} hg/ha` 
        - **RMSE (erreur quadratique moyenne)** : `{rmse:.2f} hg/ha` 
        - **R² (coefficient de détermination)** : `{r2:.2f}`

        ## ℹ️ Interprétation

        - **MAE** indique l’erreur moyenne réelle du modèle. 
        - **RMSE** pénalise davantage les grosses erreurs. 
        - **R²** mesure la proportion de variance expliquée par le modèle.
        """)

# --------------------------------------------------------------
# LANCEMENT

interface.launch(theme=theme)
