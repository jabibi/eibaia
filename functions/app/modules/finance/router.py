from fastapi import APIRouter, Depends, HTTPException, status as http_status

from app.core.security import CurrentUser, require_role

from . import services
from .schemas import (
    FinanceSummaryOut,
    MovementIn,
    MovementListOut,
    MovementOut,
    MovementScope,
    MovementStatus,
    MovementUpdateIn,
    StatusUpdateIn,
)

router = APIRouter(prefix="/finance", tags=["finance"])

_ANY_ROLE = require_role("admin", "manager", "user")
_MUTABLE_STATUSES = ("draft", "confirmed")


def _get_movement_or_404(movement_id: str):
    doc = services.get_movement(movement_id)
    if doc is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Movement not found")
    return doc


def _can_mutate(user: CurrentUser, data: dict) -> bool:
    """Owner can edit/delete their own draft. A manager/admin can edit/delete any
    draft or confirmed movement."""
    if data["status"] not in _MUTABLE_STATUSES:
        return False
    if user.role in ("admin", "manager"):
        return True
    return data["created_by"] == user.uid and data["status"] == "draft"


@router.get("/summary", response_model=FinanceSummaryOut)
def read_summary(_user: CurrentUser = Depends(_ANY_ROLE)):
    return services.get_summary()


@router.get("/movements", response_model=MovementListOut)
def list_movements(
    page_token: str | None = None,
    status: MovementStatus | None = None,
    scope: MovementScope | None = None,
    _user: CurrentUser = Depends(_ANY_ROLE),
):
    movements, next_page_token = services.list_movements(page_token=page_token, status=status, scope=scope)
    return MovementListOut(movements=movements, next_page_token=next_page_token)


@router.get("/movements/{movement_id}", response_model=MovementOut)
def read_movement(movement_id: str, _user: CurrentUser = Depends(_ANY_ROLE)):
    doc = _get_movement_or_404(movement_id)
    return services.doc_to_out(doc)


@router.post("/movements", response_model=MovementOut)
def create_movement(payload: MovementIn, user: CurrentUser = Depends(_ANY_ROLE)):
    try:
        return services.create_movement(payload, uid=user.uid, display_name=user.name)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/movements/{movement_id}", response_model=MovementOut)
def update_movement(movement_id: str, payload: MovementUpdateIn, user: CurrentUser = Depends(_ANY_ROLE)):
    doc = _get_movement_or_404(movement_id)
    data = doc.to_dict()

    if not _can_mutate(user, data):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="You can't edit this movement")

    try:
        return services.update_movement(movement_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/movements/{movement_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_movement(movement_id: str, user: CurrentUser = Depends(_ANY_ROLE)):
    doc = _get_movement_or_404(movement_id)
    data = doc.to_dict()

    if not _can_mutate(user, data):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="You can't delete this movement")

    services.delete_movement(movement_id)


@router.patch("/movements/{movement_id}/status", response_model=MovementOut)
def confirm_movement(movement_id: str, payload: StatusUpdateIn, user: CurrentUser = Depends(_ANY_ROLE)):
    doc = _get_movement_or_404(movement_id)
    data = doc.to_dict()

    if user.role not in ("admin", "manager"):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Only a manager can confirm a movement")
    if data["status"] != "draft":
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="Only draft movements can be confirmed")

    return services.confirm_movement(movement_id, user.uid)
