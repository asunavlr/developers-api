from fastapi import APIRouter, HTTPException
from ..schemas import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    LoginResponse,
    UserBasic,
)
from ..deps.supabase_client import get_anon_client, get_service_client

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, responses={
    400: {"description": "Erro ao registrar"},
    422: {"description": "Erro de validação"},
})
def register(payload: RegisterRequest):
    email = payload.email
    password = payload.password
    name = payload.name
    phone = payload.phone

    anon_client = get_anon_client()
    try:
        res = anon_client.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        # Erros de validação do Supabase (e.g., email inválido)
        raise HTTPException(status_code=400, detail=str(e))
    user = getattr(res, "user", None)
    error = getattr(res, "error", None)
    if error:
        raise HTTPException(status_code=400, detail=str(error))
    if user is None:
        raise HTTPException(status_code=400, detail="Falha ao cadastrar usuário")

    # gotrue retorna um modelo; extrair id com segurança
    user_id = getattr(user, "id", None)
    if user_id is None and isinstance(user, dict):
        user_id = user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Falha ao obter ID do usuário")

    # Inserir na tabela users
    service_client = get_service_client()
    db = service_client or anon_client
    inserted = db.table("users").insert(
        {"id": user_id, "name": name, "email": email, "phone": phone, "status": "active"}
    ).execute()
    if getattr(inserted, "error", None):
        raise HTTPException(status_code=400, detail=str(inserted.error))

    # Seleciona os campos
    result = db.table("users").select("id,name,email").eq("id", user_id).single().execute()
    if getattr(result, "error", None):
        raise HTTPException(status_code=400, detail=str(result.error))

    return {"message": "Usuário cadastrado com sucesso", "user": UserBasic(**result.data)}


@router.post("/login", response_model=LoginResponse, responses={
    400: {"description": "Erro ao autenticar"},
    422: {"description": "Erro de validação"},
})
def login(payload: LoginRequest):
    email = payload.email
    password = payload.password

    anon_client = get_anon_client()
    try:
        res = anon_client.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as e:
        # Erros comuns: Email not confirmed, invalid credentials
        raise HTTPException(status_code=400, detail=str(e))
    session = getattr(res, "session", None)
    if session is None:
        raise HTTPException(status_code=400, detail="Login falhou: sessão não retornada")

    # Extrai tokens considerando modelo pydantic
    access_token = getattr(session, "access_token", None)
    refresh_token = getattr(session, "refresh_token", None)
    if access_token is None and isinstance(session, dict):
        access_token = session.get("access_token")
        refresh_token = session.get("refresh_token")

    service_client = get_service_client()
    db = service_client or anon_client
    profile = db.table("users").select("id,email,name").eq("email", email).single().execute()
    if getattr(profile, "error", None):
        raise HTTPException(status_code=400, detail=str(profile.error))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": UserBasic(**profile.data),
    }