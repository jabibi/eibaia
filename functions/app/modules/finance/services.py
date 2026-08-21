from datetime import date

from firebase_admin import firestore

from app.core.firebase import get_db

from .schemas import (
    FinanceSummaryOut,
    MonthlyStatOut,
    MovementIn,
    MovementOut,
    MovementScope,
    MovementStatus,
    MovementType,
    PaymentMethod,
    MovementUpdateIn,
)

COLLECTION = "finance_movements"


def _affects_cash(type_: MovementType, method: PaymentMethod | None) -> bool:
    """Whether a movement moves the cash safe balance. Only card expenses don't."""
    return not (type_ == "expense" and method == "card")


def validate_business_rules(type_: MovementType, method: PaymentMethod | None, amount_cents: int) -> None:
    if type_ == "expense":
        if method is None:
            raise ValueError("method is required for expense movements")
        if amount_cents <= 0:
            raise ValueError("expense amount must be positive")
    elif type_ == "income":
        if method is not None:
            raise ValueError("method is not applicable for income movements")
        if amount_cents <= 0:
            raise ValueError("income amount must be positive")
    elif type_ == "adjustment":
        if method is not None:
            raise ValueError("method is not applicable for adjustment movements")
        if amount_cents == 0:
            raise ValueError("adjustment amount cannot be zero")


def _signed_amount(type_: MovementType, method: PaymentMethod | None, amount_cents: int) -> int:
    if type_ == "expense":
        return -amount_cents if method == "cash" else 0
    return amount_cents  # income and adjustment are already signed as stored


def _isoformat(value) -> str | None:
    return value.isoformat() if value is not None else None


def doc_to_out(doc) -> MovementOut:
    data = doc.to_dict()
    return MovementOut(
        id=doc.id,
        type=data["type"],
        method=data.get("method"),
        amount_cents=data["amount_cents"],
        description=data["description"],
        date=data["date"],
        status=data["status"],
        created_by=data["created_by"],
        created_by_name=data.get("created_by_name"),
        created_at=_isoformat(data.get("created_at")),
        reviewed_by=data.get("reviewed_by"),
        reviewed_at=_isoformat(data.get("reviewed_at")),
    )


def create_movement(payload: MovementIn, uid: str, display_name: str | None) -> MovementOut:
    validate_business_rules(payload.type, payload.method, payload.amount_cents)

    db = get_db()
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set(
        {
            "type": payload.type,
            "method": payload.method,
            "amount_cents": payload.amount_cents,
            "description": payload.description,
            "date": payload.date.isoformat(),
            "status": "draft",
            "created_by": uid,
            "created_by_name": display_name,
            "created_at": firestore.SERVER_TIMESTAMP,
            "affects_cash": _affects_cash(payload.type, payload.method),
        }
    )
    return doc_to_out(doc_ref.get())


def get_movement(movement_id: str):
    db = get_db()
    doc = db.collection(COLLECTION).document(movement_id).get()
    return doc if doc.exists else None


def delete_movement(movement_id: str) -> None:
    get_db().collection(COLLECTION).document(movement_id).delete()


def update_movement(movement_id: str, payload: MovementUpdateIn) -> MovementOut:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(movement_id)
    existing = doc_ref.get().to_dict()

    merged_type = payload.type or existing["type"]
    merged_method = payload.method if payload.method is not None else existing.get("method")
    merged_amount = payload.amount_cents if payload.amount_cents is not None else existing["amount_cents"]
    validate_business_rules(merged_type, merged_method, merged_amount)

    updates = {
        "type": merged_type,
        "method": merged_method,
        "amount_cents": merged_amount,
        "affects_cash": _affects_cash(merged_type, merged_method),
    }
    if payload.description is not None:
        updates["description"] = payload.description
    if payload.date is not None:
        updates["date"] = payload.date.isoformat()

    doc_ref.update(updates)
    return doc_to_out(doc_ref.get())


def confirm_movement(movement_id: str, reviewer_uid: str) -> MovementOut:
    db = get_db()
    doc_ref = db.collection(COLLECTION).document(movement_id)
    doc_ref.update({"status": "confirmed", "reviewed_by": reviewer_uid, "reviewed_at": firestore.SERVER_TIMESTAMP})
    return doc_to_out(doc_ref.get())


def list_movements(
    page_size: int = 20,
    page_token: str | None = None,
    status: MovementStatus | None = None,
    scope: MovementScope | None = None,
) -> tuple[list[MovementOut], str | None]:
    db = get_db()
    query = db.collection(COLLECTION)
    if status is not None:
        query = query.where(filter=firestore.FieldFilter("status", "==", status))
    if scope is not None:
        query = query.where(filter=firestore.FieldFilter("affects_cash", "==", scope == "cash"))
    query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

    if page_token:
        cursor_doc = db.collection(COLLECTION).document(page_token).get()
        if cursor_doc.exists:
            query = query.start_after(cursor_doc)

    docs = list(query.limit(page_size).stream())
    next_page_token = docs[-1].id if len(docs) == page_size else None
    return [doc_to_out(doc) for doc in docs], next_page_token


def get_summary() -> FinanceSummaryOut:
    db = get_db()
    docs = db.collection(COLLECTION).stream()
    current_month = date.today().strftime("%Y-%m")

    balance_cents = 0
    cash_total, cash_count = 0, 0
    card_total, card_count = 0, 0
    pending_drafts = 0

    for doc in docs:
        data = doc.to_dict()
        type_ = data["type"]
        method = data.get("method")
        amount = data["amount_cents"]

        balance_cents += _signed_amount(type_, method, amount)
        if data["status"] == "draft":
            pending_drafts += 1

        if type_ == "expense" and data["date"].startswith(current_month):
            if method == "cash":
                cash_total += amount
                cash_count += 1
            elif method == "card":
                card_total += amount
                card_count += 1

    return FinanceSummaryOut(
        balance_cents=balance_cents,
        cash_expenses_month=MonthlyStatOut(total_cents=cash_total, count=cash_count),
        card_expenses_month=MonthlyStatOut(total_cents=card_total, count=card_count),
        pending_drafts_count=pending_drafts,
    )
