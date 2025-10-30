from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from ..schemas import (
    UpdateUserRequest,
    StatusPatchRequest,
    UpdateUserResponse,
    UserMeResponse,
    StatusPatchResponse,
    UserBasic,
)
from ..deps.supabase_client import get_anon_client, get_service_client
from ..utils.auth import get_user_from_token

router = APIRouter()


@router.put("/{id}", response_model=UpdateUserResponse, responses={
    400: {"description": "Erro na atualização"},
    401: {"description": "Token não fornecido"},
    403: {"description": "Acesso negado"},
    422: {"description": "Erro de validação"},
})
def update_user(id: str, payload: UpdateUserRequest, authorization: Optional[str] = Header(None)):
    auth_user = get_user_from_token(authorization)
    auth_user_id = auth_user.get("id")
    if not auth_user_id or auth_user_id != id:
        raise HTTPException(status_code=403, detail="Você só pode atualizar seus próprios dados")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="É necessário enviar pelo menos um campo para atualizar")

    anon_client = get_anon_client()
    service_client = get_service_client()
    db = service_client or anon_client
    # supabase-py não suporta select encadeado após update no builder sync
    upd = db.table("users").update(updates).eq("id", auth_user_id).execute()
    if getattr(upd, "error", None):
        raise HTTPException(status_code=400, detail=str(upd.error))
    res = db.table("users").select(
        "id,name,email,phone,status,updated_at"
    ).eq("id", auth_user_id).single().execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=400, detail=str(res.error))
    return {"message": "Usuário atualizado com sucesso", "user": UserBasic(**res.data)}


@router.get("/me", response_model=UserMeResponse, responses={
    401: {"description": "Token não fornecido"},
})
def me(authorization: Optional[str] = Header(None)):
    auth_user = get_user_from_token(authorization)
    auth_user_id = auth_user.get("id")
    anon_client = get_anon_client()
    service_client = get_service_client()
    db = service_client or anon_client
    res = db.table("users").select(
        "id,name,email,phone,status,created_at,updated_at,role"
    ).eq("id", auth_user_id).single().execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=400, detail=str(res.error))
    return UserBasic(**res.data)


@router.patch("/{id}/status", response_model=StatusPatchResponse, responses={
    400: {"description": "Erro na atualização de status"},
    401: {"description": "Token não fornecido"},
    403: {"description": "Acesso negado"},
    422: {"description": "Erro de validação"},
})
def patch_status(id: str, payload: StatusPatchRequest, authorization: Optional[str] = Header(None)):
    auth_user = get_user_from_token(authorization)
    auth_user_id = auth_user.get("id")
    anon_client = get_anon_client()
    service_client = get_service_client()
    db = service_client or anon_client
    me = db.table("users").select("id,role").eq("id", auth_user_id).single().execute()
    if getattr(me, "error", None):
        raise HTTPException(status_code=400, detail=str(me.error))
    if me.data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado: requer role admin")

    upd = db.table("users").update({"status": payload.status}).eq("id", id).execute()
    if getattr(upd, "error", None):
        raise HTTPException(status_code=400, detail=str(upd.error))
    res = db.table("users").select("id,status").eq("id", id).single().execute()
    if getattr(res, "error", None):
        raise HTTPException(status_code=400, detail=str(res.error))
    return {"message": "Status atualizado com sucesso", "user": UserBasic(**res.data)}