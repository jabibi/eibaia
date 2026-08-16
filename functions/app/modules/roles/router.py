from fastapi import APIRouter, Depends, HTTPException, status as http_status

from app.core.security import CurrentUser, require_permission

from . import services
from .schemas import PermissionGroupOut, UserRoleCreateIn, UserRoleOut

router = APIRouter(tags=["roles"])
_ADMIN = require_permission("SYSTEM_ADMIN")


@router.get("/roles", response_model=list[UserRoleOut])
def list_roles(_user: CurrentUser = Depends(_ADMIN)):
    return services.list_roles()


@router.post("/roles", response_model=UserRoleOut, status_code=http_status.HTTP_201_CREATED)
def create_role(payload: UserRoleCreateIn, _user: CurrentUser = Depends(_ADMIN)):
    try:
        return services.create_role(payload)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/permission-groups", response_model=list[PermissionGroupOut])
def list_permission_groups(_user: CurrentUser = Depends(_ADMIN)):
    return services.list_permission_groups()
