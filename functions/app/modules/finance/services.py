from datetime import date

from firebase_admin import firestore

from app.core.firebase import get_db, snapshot_data

from .schemas import (
    CashboxIn,
    CashboxOut,
    CategoryColor,
    CategoryIn,
    CategoryOut,
    FinanceSummaryOut,
    MonthlyStatOut,
    MovementIn,
    MovementOut,
    MovementStatus,
    MovementType,
    PaymentMethod,
    MovementUpdateIn,
    ReportOut,
    ReportTotalsOut,
)

MOVEMENT_COLLECTION = "cashbox_movement"
CASHBOX_COLLECTION = "cashbox"
CATEGORY_COLLECTION = "cashbox_movement_category"

DEFAULT_CASHBOX_NAME = "Caja"
DEFAULT_CATEGORY_COLOR: CategoryColor = "blue"


def validate_business_rules(
    method: PaymentMethod | None, amount_cents: int, cashbox_id: str | None, category_id: str | None
) -> None:
    if method is None:
        raise ValueError("method is required")
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    if cashbox_id is None:
        raise ValueError("cashbox_id is required")
    if category_id is None:
        raise ValueError("category_id is required")
    if get_category(category_id) is None:
        raise ValueError("category not found")


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
        category_id=data.get("category_id"),
        worker_name=data.get("worker_name"),
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
        ribbon_label=data.get("ribbon_label"),
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


def set_cashbox_ribbon_label(cashbox_id: str, ribbon_label: str | None) -> CashboxOut:
    """Used only by scripts/set_cashbox_ribbon_label.py — no HTTP endpoint exposes this on
    purpose, since it's an environment marker (e.g. "TEST") set by hand per Firestore
    project, never something a user edits from the app."""
    doc_ref = get_db().collection(CASHBOX_COLLECTION).document(cashbox_id)
    doc_ref.update({"ribbon_label": ribbon_label})
    return cashbox_doc_to_out(doc_ref.get())


def get_cashbox(cashbox_id: str):
    db = get_db()
    doc = db.collection(CASHBOX_COLLECTION).document(cashbox_id).get()
    return doc if doc.exists else None


def category_doc_to_out(doc) -> CategoryOut:
    data = snapshot_data(doc)
    return CategoryOut(id=doc.id, name=data["name"], color=data.get("color", DEFAULT_CATEGORY_COLOR))


def list_categories() -> list[CategoryOut]:
    db = get_db()
    docs = db.collection(CATEGORY_COLLECTION).order_by("name").stream()
    return [category_doc_to_out(doc) for doc in docs]


def get_category(category_id: str):
    db = get_db()
    doc = db.collection(CATEGORY_COLLECTION).document(category_id).get()
    return doc if doc.exists else None


def create_category(payload: CategoryIn) -> CategoryOut:
    db = get_db()
    doc_ref = db.collection(CATEGORY_COLLECTION).document()
    doc_ref.set({"name": payload.name, "color": payload.color})
    return category_doc_to_out(doc_ref.get())


def update_category(category_id: str, payload: CategoryIn) -> CategoryOut:
    db = get_db()
    doc_ref = db.collection(CATEGORY_COLLECTION).document(category_id)
    if not doc_ref.get().exists:
        raise ValueError("category not found")
    doc_ref.update({"name": payload.name, "color": payload.color})
    return category_doc_to_out(doc_ref.get())


def delete_category(category_id: str) -> None:
    get_db().collection(CATEGORY_COLLECTION).document(category_id).delete()


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
    validate_business_rules(payload.method, payload.amount_cents, payload.cashbox_id, payload.category_id)
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
            "category_id": payload.category_id,
            "worker_name": payload.worker_name,
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
    merged_category_id = payload.category_id if payload.category_id is not None else existing.get("category_id")
    validate_business_rules(merged_method, merged_amount, merged_cashbox_id, merged_category_id)
    assert merged_cashbox_id is not None  # guaranteed by validate_business_rules
    if get_cashbox(merged_cashbox_id) is None:
        raise ValueError("cashbox not found")

    updates = {
        "type": merged_type,
        "method": merged_method,
        "cashbox_id": merged_cashbox_id,
        "category_id": merged_category_id,
        "amount_cents": merged_amount,
    }
    if payload.worker_name is not None:
        updates["worker_name"] = payload.worker_name
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


def get_report(
    date_from: date, date_to: date, scope: PaymentMethod | None, category_id: str | None
) -> ReportOut:
    if date_from > date_to:
        raise ValueError("date_from must not be after date_to")

    db = get_db()
    query = (
        db.collection(MOVEMENT_COLLECTION)
        .where(filter=firestore.FieldFilter("status", "==", "confirmed"))
        .where(filter=firestore.FieldFilter("date", ">=", date_from.isoformat()))
        .where(filter=firestore.FieldFilter("date", "<=", date_to.isoformat()))
        .order_by("date")
    )

    movements: list[MovementOut] = []
    income_cents, expense_cents = 0, 0
    for doc in query.stream():
        data = snapshot_data(doc)
        if scope is not None and data.get("method") != scope:
            continue
        if category_id is not None and data.get("category_id") != category_id:
            continue

        movements.append(doc_to_out(doc))
        if data["type"] == "income":
            income_cents += data["amount_cents"]
        else:
            expense_cents += data["amount_cents"]

    return ReportOut(
        movements=movements,
        totals=ReportTotalsOut(
            income_cents=income_cents,
            expense_cents=expense_cents,
            net_cents=income_cents - expense_cents,
        ),
    )
