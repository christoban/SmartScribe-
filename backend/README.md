# SmartScribe (Backend)

Backend FastAPI + Celery (Redis) + MongoDB pour SmartScribe / SmartScribe Multimodal.

## Démarrage rapide (local)

1. Installer les dépendances

```bash
pip install -r requirements.txt
```

2. Créer un `.env` à la racine de `backend/` (variables minimales)

- `MONGO_URI`
- `JWT_SECRET_KEY`
- `GROQ_API_KEY`
- `REDIS_URL` (optionnel, défaut: `redis://localhost:6379/0`)

3. Lancer l’API

```bash
uvicorn app.main:app --reload
```

4. Lancer le worker Celery

```bash
celery -A app.core.celery_app worker --loglevel=info
```

## Architecture

Le code suit la séparation:

- `app/api/` (HTTP)
- `app/services/` (métier/IA/media/export)
- `app/db/` (Mongo + repositories)
- `app/models/`, `app/schemas/` (DB / API)

