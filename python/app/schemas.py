from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    # mínimo 8, ao menos uma minúscula, maiúscula e dígito
    password: str = Field(
        min_length=8,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$",
    )
    name: str = Field(min_length=2)
    # Formato E.164 básico
    phone: str = Field(pattern=r"^\+?[1-9]\d{7,14}$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, pattern=r"^\+?[1-9]\d{7,14}$")


class StatusPatchRequest(BaseModel):
    status: str = Field(pattern=r"^(active|inactive|blocked)$")


# Response models para documentação
class UserBasic(BaseModel):
    id: str
    email: EmailStr | None = None
    name: str | None = None
    phone: str | None = None
    status: str | None = None
    role: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class RegisterResponse(BaseModel):
    message: str
    user: UserBasic


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    user: UserBasic


class UpdateUserResponse(BaseModel):
    message: str
    user: UserBasic


class UserMeResponse(UserBasic):
    pass


class StatusPatchResponse(BaseModel):
    message: str
    user: UserBasic