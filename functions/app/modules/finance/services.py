from firebase_admin import firestore

from app.core.firebase import get_db

from .schemas import MovementIn, MovementOut, MovementStatus, MovementType, PaymentMethod, MovementUpdateIn

COLLECTION = "finance_movements"


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

    updates = {"type": merged_type, "method": merged_method, "amount_cents": merged_amount}
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


def get_balance_cents() -> int:
    db = get_db()
    docs = db.collection(COLLECTION).stream()
    total = 0
    for doc in docs:
        data = doc.to_dict()
        total += _signed_amount(data["type"], data.get("method"), data["amount_cents"])
    return total


def list_recent(limit: int = 10) -> list[MovementOut]:
    db = get_db()
    query = db.collection(COLLECTION).order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
    return [doc_to_out(doc) for doc in query.stream()]


def list_movements(
    page_size: int = 20, page_token: str | None = None, status: MovementStatus | None = None
) -> tuple[list[MovementOut], str | None]:
    db = get_db()
    query = db.collection(COLLECTION)
    if status is not None:
        query = query.where("status", "==", status)
    query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

    if page_token:
        cursor_doc = db.collection(COLLECTION).document(page_token).get()
        if cursor_doc.exists:
            query = query.start_after(cursor_doc)

    docs = list(query.limit(page_size).stream())
    next_page_token = docs[-1].id if len(docs) == page_size else None
    return [doc_to_out(doc) for doc in docs], next_page_token
