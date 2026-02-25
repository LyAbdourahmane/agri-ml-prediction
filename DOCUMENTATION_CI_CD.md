# Documentation CI/CD - Agriculture Yield Prediction

Ce document détaille le fonctionnement du pipeline d'intégration et de déploiement continu automatisé pour le projet **agri-ml-prediction**.

## Architecture du Pipeline

Le pipeline est orchestré par **GitHub Actions** (`.github/workflows/ci_cd.yaml`) et se divise en 4 étapes majeures :

### 1. Phase de Test (CI)
- **Environnement** : Ubuntu Latest, Python 3.12.
- **Outil** : `uv` (Astral) pour une installation instantanée des dépendances.
- **Action** : 
    - `uv sync --frozen` : Installe exactement les versions du fichier lock.
    - `uv run pytest` : Exécute les 16 tests unitaires et d'intégration.
- **Sécurité** : Une clé API de test est injectée via `conftest.py`.

### 2. Build & Push - API Backend
- **Déclencheur** : Push sur `main`.
- **Dockerfile** : Utilise un build multi-étape avec `uv` pour une image légère et sécurisée.
- **Registre** : DockerHub.
- **Image** : `votre-user/agri-api:latest`.

### 3. Build & Push - Frontend UI
- **Déclencheur** : Push sur `main`.
- **Dockerfile** : `Dockerfile.frontend`.
- **Registre** : DockerHub.
- **Image** : `votre-user/agri-frontend:latest`.

### 4. Déploiement (CD)
- **Cible** : Render.com.
- **Méthode** : Webhooks (Deploy Hooks).
- **Condition** : Uniquement si les phases précédentes (Tests + Builds) sont un succès.

---

## 🔐 Configuration des Secrets GitHub

Pour activer le pipeline, configurez les secrets suivants dans `Settings > Secrets and variables > Actions` :

| Nom du Secret | Usage |
| :--- | :--- |
| `DOCKERHUB_USERNAME` | Identifiant DockerHub pour le push des images. |
| `DOCKERHUB_TOKEN` | Token d'accès personnel DockerHub. |
| `RENDER_API_DEPLOY_HOOK` | URL de déploiement fournie par Render pour le Backend. |
| `RENDER_FRONTEND_DEPLOY_HOOK` | URL de déploiement fournie par Render pour le Frontend. |

---

## 🌍 Déploiement sur Render

### Variables d'Environnement Requises

Lors de la configuration de vos services sur Render, assurez-vous d'ajouter :

#### Backend (API)
- `API_KEY` : (Obligatoire) Clé de sécurité pour protéger les prédictions.
- `PORT` : `8000`.

#### Frontend (Gradio)
- `API_KEY` : (Obligatoire) Doit correspondre à celle du Backend.
- `API_URL` : URL publique du Backend (ex: `https://agri-api.onrender.com`).
- `PORT` : `7860`.

---

## 🛠️ Maintenance du Pipeline

- **Mise à jour des dépendances** : Utilisez `uv add <package>` en local, puis committez le fichier `uv.lock`. Le pipeline utilisera automatiquement les nouvelles versions.
- **Échecs des tests** : Si un test échoue en CI, le build Docker ne sera pas lancé, garantissant qu'aucune version défectueuse n'arrive en production.

---

**Dépôt Officiel** : [https://github.com/LyAbdourahmane/agri-ml-prediction](https://github.com/LyAbdourahmane/agri-ml-prediction)
