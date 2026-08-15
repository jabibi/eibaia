from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, require_role

from . import services

router = APIRouter(prefix="/system", tags=["system"])


@router.post("/reset")
def factory_reset(_user: CurrentUser = Depends(require_role("admin"))):
    services.factory_reset()
    return {"status": "ok"}
