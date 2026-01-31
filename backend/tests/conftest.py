import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.db.mongo import get_database, connect_to_mongo, close_mongo_connection

@pytest.fixture(scope="session")
def event_loop():
    """Crée une instance de la boucle d'événements pour toute la session de test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def db_setup():
    """Connecte et déconnecte la DB de test proprement."""
    await connect_to_mongo()
    yield
    # Optionnel : Tu pourrais vider la DB de test ici
    await close_mongo_connection()

@pytest.fixture
async def client():
    """Fournit un client HTTP asynchrone pour tes endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac