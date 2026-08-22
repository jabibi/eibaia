from datetime import date

from firebase_admin import firestore

from app.core.firebase import get_db, snapshot_data

from .schemas import (
    CashboxIn,
    CashboxOut,
    FinanceSummaryOut,
    LabelColor,
    LabelIn,
    LabelOut,
    MonthlyStatOut,
    MovementIn,
    MovementOut,
    MovementStatus,
    MovementType,
    PaymentMethod,
    MovementUpdateIn,
)

MOVEMENT_COLLECTION = "cashbox_movement"
CASHBOX_COLLECTION = "cashbox"
LABEL_COLLECTION = "cashbox_movement_label"

DEFAULT_CASHBOX_NAME = "Caja"
DEFAULT_LABEL_COLOR: LabelColor = "blue"


def validate_business_rules(
    method: PaymentMethod | None, amount_cents: int, cashbox_id: str | None, label_id: str | None
) -> None:
    if method is None:
        raise ValueError("method is required")
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    if cashbox_id is None:
        raise ValueError("cashbox_id is required")
    if label_id is None:
        raise ValueError("label_id is required")
    if get_label(label_id) is None:
        raise ValueError("label not found")


def _signed_amount(type_: MovementType, amount_cents: int) -> int:
    return -amount_cents if type_ == "expense" else amount_cents


def _isoformat(value) -> str | None:
    return value.isoformat() if value is not None else None


def doc_to_out(doc) -> MovementOut:
    data = snapshot_data(doc)
    return MovementOut(
        id=doc.id,
        type=data["type"],
        method=data.get("method"),
        cashbox_id=data.get("cashbox_id"),
        label_id=data.get("label_id"),
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


def cashbox_doc_to_out(doc) -> CashboxOut:
    data = snapshot_data(doc)
    return CashboxOut(
        id=doc.id,
        name=data["name"],
        total_amount_cents=data["total_amount_cents"],
        last_update=_isoformat(data.get("last_update")),
    )


def create_cashbox(payload: CashboxIn) -> CashboxOut:
    db = get_db()
    doc_ref = db.collection(CASHBOX_COLLECTION).document()
    doc_ref.set({"name": payload.name, "total_amount_cents": 0, "last_update": firestore.SERVER_TIMESTAMP})
    return cashbox_doc_to_out(doc_ref.get())


def list_cashboxes() -> list[CashboxOut]:
    db = get_db()
    docs = db.collection(CASHBOX_COLLECTION).order_by("name").stream()
    return [cashbox_doc_to_out(doc) for doc in docs]


def get_cashbox(cashbox_id: str):
    db = get_db()
    doc = db.collection(CASHBOX_COLLECTION).document(cashbox_id).get()
    return doc if doc.exists else None


def label_doc_to_out(doc) -> LabelOut:
    data = snapshot_data(doc)
    return LabelOut(id=doc.id, name=data["name"], color=data.get("color", DEFAULT_LABEL_COLOR))


def list_labels() -> list[LabelOut]:
    db = get_db()
    docs = db.collection(LABEL_COLLECTION).order_by("name").stream()
    return [label_doc_to_out(doc) for doc in docs]


def get_label(label_id: str):
    db = get_db()
    doc = db.collection(LABEL_COLLECTION).document(label_id).get()
    return doc if doc.exists else None


def create_label(payload: LabelIn) -> LabelOut:
    db = get_db()
    doc_ref = db.collection(LABEL_COLLECTION).document()
    doc_ref.set({"name": payload.name, "color": payload.color})
    return label_doc_to_out(doc_ref.get())


def update_label(label_id: str, payload: LabelIn) -> LabelOut:
    db = get_db()
    doc_ref = db.collection(LABEL_COLLECTION).document(label_id)
    if not doc_ref.get().exists:
        raise ValueError("label not found")
    doc_ref.update({"name": payload.name, "color": payload.color})
    return label_doc_to_out(doc_ref.get())


def delete_label(label_id: str) -> None:
    get_db().collection(LABEL_COLLECTION).document(label_id).delete()


def seed_defaults() -> None:
    """Creates the default cashbox if none exists yet. Idempotent — safe to
    call on an existing project (e.g. after a factory reset) as well as a
    brand new one."""
    if not list_cashboxes():
        create_cashbox(CashboxIn(name=DEFAULT_CASHBOX_NAME))


def _adjust_cashbox_total(db, cashbox_id: str, delta_cents: int) -> None:
    db.collection(CASHBOX_COLLECTION).document(cashbox_id).update(
        {"total_amount_cents": firestore.Increment(delta_cents), "last_update": firestore.SERVER_TIMESTAMP}
    )


def create_movement(payload: MovementIn, uid: str, display_name: str | None) -> MovementOut:
    validate_business_rules(payload.method, payload.amount_cents, payload.cashbox_id, payload.label_id)
    assert payload.cashbox_id is not None  # guaranteed by validate_business_rules
    if get_cashbox(payload.cashbox_id) is None:
        raise ValueError("cashbox not found")

    db = get_db()
    doc_ref = db.collection(MOVEMENT_COLLECTION).document()
    doc_ref.set(
        {
            "type": payload.type,
            "method": payload.method,
            "cashbox_id": payload.cashbox_id,
            "label_id": payload.label_id,
            "amount_cents": payload.amount_cents,
            "description": payload.description,
            "date": payload.date.isoformat(),
            "status": "draft",
            "created_by": uid,
            "created_by_name": display_name,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
    )
    if payload.method == "cash":
        _adjust_cashbox_total(db, payload.cashbox_id, _signed_amount(payload.type, payload.amount_cents))
    return doc_to_out(doc_ref.get())


def get_movement(movement_id: str):
    db = get_db()
    doc = db.collection(MOVEMENT_COLLECTION).document(movement_id).get()
    return doc if doc.exists else None


def delete_movement(movement_id: str) -> None:
    db = get_db()
    doc_ref = db.collection(MOVEMENT_COLLECTION).document(movement_id)
    existing = snapshot_data(doc_ref.get())
    doc_ref.delete()
    if existing.get("method") == "cash":
        _adjust_cashbox_total(db, existing["cashbox_id"], -_signed_amount(existing["type"], existing["amount_cents"]))


def update_movement(movement_id: str, payload: MovementUpdateIn) -> MovementOut:
    db = get_db()
    doc_ref = db.collection(MOVEMENT_COLLECTION).document(movement_id)
    existing = snapshot_data(doc_ref.get())

    merged_type = payload.type or existing["type"]
    merged_method = payload.method if payload.method is not None else existing.get("method")
    merged_amount = payload.amount_cents if payload.amount_cents is not None else existing["amount_cents"]
    merged_cashbox_id = payload.cashbox_id if payload.cashbox_id is not None else existing.get("cashbox_id")
    merged_label_id = payload.label_id if payload.label_id is not None else existing.get("label_id")
    validate_business_rules(merged_method, merged_amount, merged_cashbox_id, merged_label_id)
    assert merged_cashbox_id is not None  # guaranteed by validate_business_rules
    if get_cashbox(merged_cashbox_id) is None:
        raise ValueError("cashbox not found")

    updates = {
        "type": merged_type,
        "method": merged_method,
        "cashbox_id": merged_cashbox_id,
        "label_id": merged_label_id,
        "amount_cents": merged_amount,
    }
    if payload.description is not None:
        updates["description"] = payload.description
    if payload.date is not None:
        updates["date"] = payload.date.isoformat()

    doc_ref.update(updates)

    if existing.get("method") == "cash":
        _adjust_cashbox_total(db, existing["cashbox_id"], -_signed_amount(existing["type"], existing["amount_cents"]))
    if merged_method == "cash":
        _adjust_cashbox_total(db, merged_cashbox_id, _signed_amount(merged_type, merged_amount))

    return doc_to_out(doc_ref.get())


def confirm_movement(movement_id: str, reviewer_uid: str) -> MovementOut:
    db = get_db()
    doc_ref = db.collection(MOVEMENT_COLLECTION).document(movement_id)
    doc_ref.update({"status": "confirmed", "reviewed_by": reviewer_uid, "reviewed_at": firestore.SERVER_TIMESTAMP})
    return doc_to_out(doc_ref.get())


def list_movements(
    page_size: int = 20,
    page_token: str | None = None,
    status: MovementStatus | None = None,
    scope: PaymentMethod | None = None,
) -> tuple[list[MovementOut], str | None]:
    db = get_db()
    query = db.collection(MOVEMENT_COLLECTION)
    if status is not None:
        query = query.where(filter=firestore.FieldFilter("status", "==", status))
    if scope is not None:
        query = query.where(filter=firestore.FieldFilter("method", "==", scope))
    query = query.order_by("created_at", direction=firestore.Query.DESCENDING)

    if page_token:
        cursor_doc = db.collection(MOVEMENT_COLLECTION).document(page_token).get()
        if cursor_doc.exists:
            query = query.start_after(cursor_doc)

    docs = list(query.limit(page_size).stream())
    next_page_token = docs[-1].id if len(docs) == page_size else None
    return [doc_to_out(doc) for doc in docs], next_page_token


def get_summary() -> FinanceSummaryOut:
    db = get_db()
    docs = db.collection(MOVEMENT_COLLECTION).stream()
    current_month = date.today().strftime("%Y-%m")

    cash_total, cash_count = 0, 0
    card_total, card_count = 0, 0
    pending_drafts = 0

    for doc in docs:
        data = snapshot_data(doc)
        type_ = data["type"]
        method = data.get("method")
        amount = data["amount_cents"]

        if data["status"] == "draft":
            pending_drafts += 1

        if type_ == "expense" and data["date"].startswith(current_month):
            if method == "cash":
                cash_total += amount
                cash_count += 1
            elif method == "card":
                card_total += amount
                card_count += 1

    balance_cents = sum(cashbox.total_amount_cents for cashbox in list_cashboxes())

    return FinanceSummaryOut(
        balance_cents=balance_cents,
        cash_expenses_month=MonthlyStatOut(total_cents=cash_total, count=cash_count),
        card_expenses_month=MonthlyStatOut(total_cents=card_total, count=card_count),
        pending_drafts_count=pending_drafts,
    )
