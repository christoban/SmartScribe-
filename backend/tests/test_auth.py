import pytest
from app.core import constants

@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    # 1. TEST INSCRIPTION
    user_data = {
        "email": "test@scolarai.fr",
        "password": "password123",
        "full_name": "Test User"
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
    assert "id" in response.json()

    # 2. TEST CONNEXION (OAuth2 form-data)
    login_data = {
        "username": "test@scolarai.fr",
        "password": "password123"
    }
    login_res = await client.post("/api/v1/auth/login", data=login_data)
    
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

    # 3. TEST ACCÈS PROTÉGÉ (Vérifie si le token fonctionne)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    # On teste sur une route protégée (ex: list media)
    protected_res = await client.get("/api/v1/media/", headers=headers)
    
    assert protected_res.status_code == 200