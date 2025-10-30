import pytest
from httpx import AsyncClient, ASGITransport
from python.app.main import app


class FakeBuilder:
    def __init__(self, data):
        self._data = data

    def select(self, *_args, **_kwargs):
        return self

    def insert(self, *_args, **_kwargs):
        return self

    def update(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def single(self):
        return self

    def execute(self):
        class R:
            def __init__(self, d):
                self.data = d
                self.error = None
        return R(self._data)


class FakeDB:
    def __init__(self, user):
        self._user = user

    def table(self, _name):
        return FakeBuilder(self._user)


@pytest.mark.asyncio
async def test_users_me_success(monkeypatch):
    # Fake token decode
    from python.app.utils import auth as auth_utils
    monkeypatch.setattr(auth_utils, "get_user_from_token", lambda bearer: {"id": "uuid-1", "email": "user@example.com"})

    # Fake DB clients
    from python.app.deps import supabase_client
    fake_user = {
        "id": "uuid-1",
        "email": "user@example.com",
        "name": "Teste",
        "phone": "+5511999999999",
        "status": "active",
    }
    monkeypatch.setattr(supabase_client, "get_anon_client", lambda: FakeDB(fake_user))
    monkeypatch.setattr(supabase_client, "get_service_client", lambda: None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/users/me", headers={"Authorization": "Bearer token"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "uuid-1"
        assert data["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_update_user_success(monkeypatch):
    from python.app.utils import auth as auth_utils
    monkeypatch.setattr(auth_utils, "get_user_from_token", lambda bearer: {"id": "uuid-1", "email": "user@example.com"})

    # Fake DB returns updated user on select
    from python.app.deps import supabase_client
    updated_user = {
        "id": "uuid-1",
        "email": "user@example.com",
        "name": "Novo Nome",
        "phone": "+5511999999999",
        "status": "active",
    }
    monkeypatch.setattr(supabase_client, "get_anon_client", lambda: FakeDB(updated_user))
    monkeypatch.setattr(supabase_client, "get_service_client", lambda: None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.put("/users/uuid-1", headers={"Authorization": "Bearer token"}, json={"name": "Novo Nome"})
        assert resp.status_code == 200
        data = resp.json()["user"]
        assert data["name"] == "Novo Nome"