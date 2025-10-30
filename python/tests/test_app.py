import pytest
from httpx import AsyncClient, ASGITransport
from python.app.main import app


@pytest.mark.asyncio
async def test_root_ok():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        assert data.get("service") == "Users API (Python)"


@pytest.mark.asyncio
async def test_users_me_requires_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/users/me")
        assert resp.status_code == 401
        assert resp.json().get("detail") == "Token não fornecido"


@pytest.mark.asyncio
async def test_put_users_requires_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.put("/users/00000000-0000-0000-0000-000000000000", json={"name": "Teste"})
        assert resp.status_code == 401
        assert resp.json().get("detail") == "Token não fornecido"


@pytest.mark.asyncio
async def test_docs_available():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/docs")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_register_validation_errors():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # email inválido
        resp = await ac.post("/auth/register", json={
            "email": "invalid",
            "password": "Senha123",
            "name": "AB",
            "phone": "+5511999999999",
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload.get("message") == "Erro de validação"

        # password fraca
        resp2 = await ac.post("/auth/register", json={
            "email": "user@example.com",
            "password": "abcdefg",  # sem dígitos e maiúsculas
            "name": "AB",
            "phone": "+5511999999999",
        })
        assert resp2.status_code == 422

        # phone inválido
        resp3 = await ac.post("/auth/register", json={
            "email": "user@example.com",
            "password": "Senha123",
            "name": "AB",
            "phone": "1199-999-999",  # não E.164
        })
        assert resp3.status_code == 422


@pytest.mark.asyncio
async def test_status_patch_validation_error():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.patch("/users/uuid/status", json={"status": "unknown"})
        assert resp.status_code == 401  # sem token cai no 401 antes do 422