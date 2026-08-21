from datetime import date as Date
from typing import Literal

from pydantic import BaseModel

MovementType = Literal["expense", "income"]
PaymentMethod = Literal["cash", "card"]
MovementStatus = Literal["draft", "confirmed"]
LabelColor = Literal[
    "red", "orange", "amber", "yellow", "lime", "green", "teal", "cyan", "blue", "indigo", "purple", "pink"
]


class MovementIn(BaseModel):
    type: MovementType
    method: PaymentMethod | None = None
    cashbox_id: str | None = None
    label_id: str | None = None
    amount_cents: int
    description: str
    date: Date


class MovementUpdateIn(BaseModel):
    type: MovementType | None = None
    method: PaymentMethod | None = None
    cashbox_id: str | None = None
    label_id: str | None = None
    amount_cents: int | None = None
    description: str | None = None
    date: Date | None = None


class StatusUpdateIn(BaseModel):
    status: Literal["confirmed"]


class MovementOut(BaseModel):
    id: str
    type: MovementType
    method: PaymentMethod | None
    cashbox_id: str | None
    label_id: str | None
    amount_cents: int
    description: str
    date: Date
    status: MovementStatus
    created_by: str
    created_by_name: str | None
    created_at: str | None
    reviewed_by: str | None = None
    reviewed_at: str | None = None


class MovementListOut(BaseModel):
    movements: list[MovementOut]
    next_page_token: str | None = None


class MonthlyStatOut(BaseModel):
    total_cents: int
    count: int


class FinanceSummaryOut(BaseModel):
    balance_cents: int
    cash_expenses_month: MonthlyStatOut
    card_expenses_month: MonthlyStatOut
    pending_drafts_count: int


class CashboxIn(BaseModel):
    name: str


class CashboxOut(BaseModel):
    id: str
    name: str
    total_amount_cents: int
    last_update: str | None


class CashboxListOut(BaseModel):
    cashboxes: list[CashboxOut]


class LabelIn(BaseModel):
    name: str
    color: LabelColor


class LabelOut(BaseModel):
    id: str
    name: str
    color: LabelColor


class LabelListOut(BaseModel):
    labels: list[LabelOut]
