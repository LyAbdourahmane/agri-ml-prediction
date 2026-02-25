# Utiliser une image Python officielle légère comme base
FROM python:3.12-slim

# Installer uv pour une gestion rapide et fiable des dépendances
# Cela garantit que nous utilisons exactement les mêmes versions que dans uv.lock
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Configuration pour uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copier les fichiers de définition des dépendances
COPY pyproject.toml uv.lock ./

# Installer les dépendances
# --frozen : utilise strictement le fichier lock sans mise à jour
# --no-install-project : installe uniquement les dépendances pour profiter du cache Docker
RUN uv sync --frozen --no-install-project

# Ajouter l'environnement virtuel au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copier le reste du code de l'application
COPY src/ ./src/
COPY model_artifacts/ ./model_artifacts/
COPY app.py .
# Note: On copie explicitement les fichiers nécessaires pour éviter d'inclure des fichiers indésirables,
# même si .dockerignore est configuré. Si vous avez d'autres fichiers (ex: dossiers de config), ajoutez-les.

# Créer un utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Exposer le port
EXPOSE 8000

# Lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
