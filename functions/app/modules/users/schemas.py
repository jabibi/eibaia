from typing import Literal

from pydantic import BaseModel

Role = Literal["admin", "manager", "user"]


class UserOut(BaseModel):
    uid: str
    email: str | None
    display_name: str | None
    photo_url: str | None
    role: Role
    disabled: bool


class UserListOut(BaseModel):
    users: list[UserOut]
    next_page_token: str | None = None


class RoleUpdateIn(BaseModel):
    role: Role
