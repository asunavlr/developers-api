from fastapi import HTTPException
from typing import Optional
from ..deps.supabase_client import get_anon_client


def get_user_from_token(bearer: Optional[str]):
    if not bearer or not bearer.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    token = bearer[len("Bearer ") :]
    # supabase-py v2
    anon_client = get_anon_client()
    try:
        res = anon_client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = getattr(res, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Token inválido")
    # Converte para dict para consumo consistente nas rotas
    data = None
    try:
        # pydantic v2
        data = user.model_dump()
    except Exception:
        data = {"id": getattr(user, "id", None), "email": getattr(user, "email", None)}
    return data