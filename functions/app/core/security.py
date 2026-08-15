"""Security middleware: Firebase Auth ID Token verification and RBAC via Custom Claims."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

from app.core import firebase as _firebase_init  # noqa: F401  (ensures the Admin SDK is initialized)

_bearer_scheme = HTTPBearer(auto_error=False)

ROLES = ("admin", "manager", "user")


@dataclass(frozen=True)
class CurrentUser:
    uid: str
    email: str | None
    name: str | None
    picture: str | None
    role: str | None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    try:
        decoded = firebase_auth.verify_id_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    role = decoded.get("role") if decoded.get("role") in ROLES else None

    return CurrentUser(
        uid=decoded["uid"],
        email=decoded.get("email"),
        name=decoded.get("name"),
        picture=decoded.get("picture"),
        role=role,
    )


def require_role(*allowed_roles: str):
    """Dependency factory: restricts the endpoint to the given roles."""

    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions to access this resource",
            )
        return user

    return dependency
