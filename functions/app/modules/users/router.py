from fastapi import APIRouter, Depends, HTTPException, status as http_status

from app.core.security import CurrentUser, get_current_user, require_permission

from . import services
from .schemas import ActiveUpdateIn, RoleUpdateIn, UserListOut, UserOut, UserStatus

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser = Depends(get_current_user)):
    role_id = user.role_id
    if role_id != "admin":
        role_id = services.ensure_first_admin(user.uid) or role_id

    return UserOut(
        uid=user.uid,
        email=user.email,
        display_name=user.name,
        photo_url=user.picture,
        role_id=role_id,
        disabled=False,
    )


@router.get("/me/permissions", response_model=list[str])
def read_my_permissions(user: CurrentUser = Depends(get_current_user)):
    return services.get_permissions_for(user.role_id)


@router.get("", response_model=UserListOut)
def list_users(
    page_token: str | None = None,
    status: UserStatus = "active",
    _user: CurrentUser = Depends(require_permission("SYSTEM_ADMIN")),
):
    users, next_page_token = services.list_users(page_token=page_token, status=status)
    return UserListOut(users=users, next_page_token=next_page_token)


@router.patch("/{uid}/role", response_model=UserOut)
def update_user_role(
    uid: str,
    payload: RoleUpdateIn,
    _user: CurrentUser = Depends(require_permission("SYSTEM_ADMIN")),
):
    try:
        return services.set_user_role(uid, payload.role_id)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{uid}/active", response_model=UserOut)
def update_user_active(
    uid: str,
    payload: ActiveUpdateIn,
    _user: CurrentUser = Depends(require_permission("SYSTEM_ADMIN")),
):
    return services.set_user_active(uid, payload.active)
