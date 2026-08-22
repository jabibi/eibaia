from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException, status as http_status

from app.core.firebase import snapshot_data
from app.core.security import CurrentUser, check_permission, require_permission

from . import services
from .schemas import (
    CashboxIn,
    CashboxListOut,
    CashboxOut,
    FinanceSummaryOut,
    LabelIn,
    LabelListOut,
    LabelOut,
    MovementIn,
    MovementListOut,
    MovementOut,
    MovementStatus,
    MovementUpdateIn,
    PaymentMethod,
    ReportOut,
    StatusUpdateIn,
)

router = APIRouter(prefix="/finance", tags=["finance"])

_BASIC = require_permission("CASHBOX_BASIC")
_MANAGE = require_permission("CASHBOX_MANAGE")
_MUTABLE_STATUSES = ("draft", "confirmed")


def _get_movement_or_404(movement_id: str):
    doc = services.get_movement(movement_id)
    if doc is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Movement not found")
    return doc


def _can_mutate(user: CurrentUser, data: dict) -> bool:
    """A user with CASHBOX_MANAGE can edit/delete any draft or confirmed movement.
    Otherwise, the owner can edit/delete their own draft (still requires CASHBOX_BASIC)."""
    if data["status"] not in _MUTABLE_STATUSES:
        return False
    if check_permission(user, "CASHBOX_MANAGE"):
        return True
    return (
        data["created_by"] == user.uid
        and data["status"] == "draft"
        and check_permission(user, "CASHBOX_BASIC")
    )


@router.get("/summary", response_model=FinanceSummaryOut)
def read_summary(_user: CurrentUser = Depends(_BASIC)):
    return services.get_summary()


@router.get("/reports", response_model=ReportOut)
def get_report(
    date_from: Date,
    date_to: Date,
    scope: PaymentMethod | None = None,
    label_id: str | None = None,
    _user: CurrentUser = Depends(_MANAGE),
):
    try:
        return services.get_report(date_from, date_to, scope, label_id)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/cashboxes", response_model=CashboxListOut)
def list_cashboxes(_user: CurrentUser = Depends(_BASIC)):
    return CashboxListOut(cashboxes=services.list_cashboxes())


@router.post("/cashboxes", response_model=CashboxOut)
def create_cashbox(payload: CashboxIn, _user: CurrentUser = Depends(_MANAGE)):
    return services.create_cashbox(payload)


@router.get("/labels", response_model=LabelListOut)
def list_labels(_user: CurrentUser = Depends(_BASIC)):
    return LabelListOut(labels=services.list_labels())


@router.post("/labels", response_model=LabelOut)
def create_label(payload: LabelIn, _user: CurrentUser = Depends(_MANAGE)):
    return services.create_label(payload)


@router.patch("/labels/{label_id}", response_model=LabelOut)
def update_label(label_id: str, payload: LabelIn, _user: CurrentUser = Depends(_MANAGE)):
    try:
        return services.update_label(label_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/labels/{label_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_label(label_id: str, _user: CurrentUser = Depends(_MANAGE)):
    services.delete_label(label_id)


@router.get("/movements", response_model=MovementListOut)
def list_movements(
    page_token: str | None = None,
    status: MovementStatus | None = None,
    scope: PaymentMethod | None = None,
    _user: CurrentUser = Depends(_BASIC),
):
    movements, next_page_token = services.list_movements(page_token=page_token, status=status, scope=scope)
    return MovementListOut(movements=movements, next_page_token=next_page_token)


@router.get("/movements/{movement_id}", response_model=MovementOut)
def read_movement(movement_id: str, _user: CurrentUser = Depends(_BASIC)):
    doc = _get_movement_or_404(movement_id)
    return services.doc_to_out(doc)


@router.post("/movements", response_model=MovementOut)
def create_movement(payload: MovementIn, user: CurrentUser = Depends(_BASIC)):
    try:
        return services.create_movement(payload, uid=user.uid, display_name=user.name)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/movements/{movement_id}", response_model=MovementOut)
def update_movement(movement_id: str, payload: MovementUpdateIn, user: CurrentUser = Depends(_BASIC)):
    doc = _get_movement_or_404(movement_id)
    data = snapshot_data(doc)

    if not _can_mutate(user, data):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="You can't edit this movement")

    try:
        return services.update_movement(movement_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/movements/{movement_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_movement(movement_id: str, user: CurrentUser = Depends(_BASIC)):
    doc = _get_movement_or_404(movement_id)
    data = snapshot_data(doc)

    if not _can_mutate(user, data):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="You can't delete this movement")

    services.delete_movement(movement_id)


@router.patch("/movements/{movement_id}/status", response_model=MovementOut)
def confirm_movement(movement_id: str, payload: StatusUpdateIn, user: CurrentUser = Depends(_BASIC)):
    doc = _get_movement_or_404(movement_id)
    data = snapshot_data(doc)

    if not check_permission(user, "CASHBOX_MANAGE"):
        raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Only a manager can confirm a movement")
    if data["status"] != "draft":
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="Only draft movements can be confirmed")

    return services.confirm_movement(movement_id, user.uid)
