"""Middleware de seguridad: verificación de ID Tokens de Firebase Auth y RBAC por Custom Claims."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

from app.core import firebase as _firebase_init  # noqa: F401  (garantiza la inicialización del Admin SDK)

_bearer_scheme = HTTPBearer(auto_error=False)

ROLES = ("admin", "manager", "user")


@dataclass(frozen=True)
class CurrentUser:
    uid: str
    email: str | None
    name: str | None
    picture: str | None
    role: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación",
        )

    try:
        decoded = firebase_auth.verify_id_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from exc

    role = decoded.get("role") if decoded.get("role") in ROLES else "user"

    return CurrentUser(
        uid=decoded["uid"],
        email=decoded.get("email"),
        name=decoded.get("name"),
        picture=decoded.get("picture"),
        role=role,
    )


def require_role(*allowed_roles: str):
    """Dependencia factory: restringe el endpoint a los roles indicados."""

    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para acceder a este recurso",
            )
        return user

    return dependency
