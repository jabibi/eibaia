"""Security middleware: Firebase Auth ID Token verification and RBAC via permission groups.

Each user's Firebase Auth custom claims carry a `role_id`, which resolves to a
`user_roles/{role_id}` Firestore document listing the permission-group codes
granted to that role.
"""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth

from app.core import firebase as _firebase_init  # noqa: F401  (ensures the Admin SDK is initialized)
from app.core.firebase import get_db, snapshot_data

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    uid: str
    email: str | None
    name: str | None
    picture: str | None
    role_id: str | None


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

    return CurrentUser(
        uid=decoded["uid"],
        email=decoded.get("email"),
        name=decoded.get("name"),
        picture=decoded.get("picture"),
        role_id=decoded.get("role_id"),
    )


def check_permission(user: CurrentUser, group_code: str) -> bool:
    """Resolves user.role_id -> user_roles/{role_id}.group_ids and checks membership."""
    if user.role_id is None:
        return False
    doc = get_db().collection("user_roles").document(user.role_id).get()
    if not doc.exists:
        return False
    return group_code in (snapshot_data(doc).get("group_ids") or [])


def require_permission(*group_codes: str):
    """Dependency factory: restricts the endpoint to users whose role grants at
    least one of the given permission-group codes."""

    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(check_permission(user, code) for code in group_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions to access this resource",
            )
        return user

    return dependency
