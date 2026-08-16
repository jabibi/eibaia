from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, require_permission

from . import services

router = APIRouter(prefix="/system", tags=["system"])


@router.post("/reset")
def factory_reset(_user: CurrentUser = Depends(require_permission("SYSTEM_ADMIN"))):
    services.factory_reset()
    return {"status": "ok"}
