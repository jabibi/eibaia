from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user, require_role

from . import services
from .schemas import ActiveUpdateIn, RoleUpdateIn, UserListOut, UserOut, UserStatus

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser = Depends(get_current_user)):
    role = user.role
    if role != "admin":
        role = services.ensure_first_admin(user.uid) or role

    return UserOut(
        uid=user.uid,
        email=user.email,
        display_name=user.name,
        photo_url=user.picture,
        role=role,
        disabled=False,
    )


@router.get("", response_model=UserListOut)
def list_users(
    page_token: str | None = None,
    status: UserStatus = "active",
    _user: CurrentUser = Depends(require_role("admin")),
):
    users, next_page_token = services.list_users(page_token=page_token, status=status)
    return UserListOut(users=users, next_page_token=next_page_token)


@router.patch("/{uid}/role", response_model=UserOut)
def update_user_role(
    uid: str,
    payload: RoleUpdateIn,
    _user: CurrentUser = Depends(require_role("admin")),
):
    return services.set_user_role(uid, payload.role)


@router.patch("/{uid}/active", response_model=UserOut)
def update_user_active(
    uid: str,
    payload: ActiveUpdateIn,
    _user: CurrentUser = Depends(require_role("admin")),
):
    return services.set_user_active(uid, payload.active)
