# 🌾 Agriculture Yield Prediction - API & Interface

Application complète de prédiction et de recommandation de rendements agricoles utilisant le Machine Learning (`RandomForest`).
L'architecture est composée d'une **API REST** (FastAPI) sécurisée et d'une **Interface Utilisateur** (Gradio) totalement découplée.

[![CI/CD Pipeline](https://github.com/LyAbdourahmane/agri-ml-prediction/actions/workflows/ci_cd.yaml/badge.svg)](https://github.com/LyAbdourahmane/agri-ml-prediction/actions)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![Package Manager](https://img.shields.io/badge/uv-Fast-BC1142)

---

## Fonctionnalités

- **Prédiction de Rendement** : Estimation précise (hg/ha) basée sur la pluviométrie, température, pesticides et type de culture.
- **Recommandation Intelligente** : Suggère la culture la plus rentable selon les conditions climatiques locales.
- **Découplage Frontend/Backend** : Le frontend récupère ses configurations (pays, cultures) dynamiquement via l'API.
- **Sécurité** : Accès aux prédictions protégé par clé API.
- **Performance** : Gestion des dépendances ultra-rapide avec `uv`.

---

## 🏗️ Architecture

L'application suit une architecture micro-services conteneurisée :

1.  **Backend (API)** : `app.py`
    - Framework : `FastAPI`
    - Gestionnaire de paquets : `uv`
    - Validation : `Pydantic V2`
    - Port : `8000`

2.  **Frontend (UI)** : `interface_gradio.py`
    - Framework : `Gradio`
    - Visualisation : `Plotly`
    - Port : `7860`
    - Communique exclusivement via l'API (aucun accès direct aux modèles).

---

## 🛠️ Installation et Lancement

### Option 1 : Avec Docker (Recommandé)

1.  **Démarrer l'API** :

    ```bash
    docker build -t agri-api -f Dockerfile .
    docker run -d --name api -p 8000:8000 -e API_KEY="votre_cle_secrete" agri-api
    ```

2.  **Démarrer le Frontend** :
    ```bash
    docker build -t agri-front -f Dockerfile.frontend .
    docker run -d --name frontend -p 7860:7860 -e API_URL="http://host.docker.internal:8000" -e API_KEY="votre_cle_secrete" agri-front
    ```

Accédez à l'interface sur : `http://localhost:7860`

---

### Option 2 : Développement local (avec `uv`)

Nous recommandons l'utilisation de [uv](https://github.com/astral-sh/uv) pour une installation rapide.

1.  **Installer les dépendances** :

    ```bash
    uv sync
    ```

2.  **Lancer l'API** :

    ```bash
    export API_KEY="votre_cle_secrete"
    uv run uvicorn app:app --reload
    ```

3.  **Lancer le Frontend** :
    ```bash
    export API_URL="http://localhost:8000"
    export API_KEY="votre_cle_secrete"
    uv run python interface_gradio.py
    ```

---

## 🧪 Tests

La suite de tests est automatisée et garantit la fiabilité du feature engineering et de l'API.

```bash
uv run pytest tests/
```

Les tests couvrent :

- ✅ **Feature Engineering** : Calculs des interactions climatiques.
- ✅ **Validation Pydantic** : Typage et contraintes métier.
- ✅ **API Endpoints** : Sécurité, prédiction et configuration dynamique.

---

## 🔄 CI/CD

Le projet utilise **GitHub Actions** pour un cycle de livraison continu :

1.  **Validation** : Tests automatisés sur Python 3.12 avec `uv`.
2.  **Conteneurisation** : Build et Push des images Docker sur DockerHub.
3.  **Déploiement** : Mise à jour automatique sur **Render**.

👉 Voir les détails : [DOCUMENTATION_CI_CD.md](DOCUMENTATION_CI_CD.md)

---

## 📂 Structure du Projet

```
.
├── .github/workflows/   # Pipeline CI/CD (GitHub Actions)
├── model_artifacts/     # Artefacts du modèle (PKL, JSON)
├── src/                 # Logique métier (Feature engineering, Pydantic)
├── tests/               # Suite de tests pytest
├── app.py               # API Backend FastAPI
├── interface_gradio.py  # Interface Frontend Gradio
├── Dockerfile           # Build API (multi-stage uv)
├── Dockerfile.frontend  # Build Frontend
├── pyproject.toml       # Configuration du projet et dépendances
└── uv.lock              # Lockfile deterministe
```

---

## 📝 Auteur

**Abdourahamane LY**  
Dépôt GitHub : [agri-ml-prediction](https://github.com/LyAbdourahmane/agri-ml-prediction)
