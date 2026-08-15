from typing import Literal

from pydantic import BaseModel

Role = Literal["admin", "manager", "user"]
UserStatus = Literal["active", "inactive", "new", "all"]


class UserOut(BaseModel):
    uid: str
    email: str | None
    display_name: str | None
    photo_url: str | None
    role: Role | None
    disabled: bool


class UserListOut(BaseModel):
    users: list[UserOut]
    next_page_token: str | None = None


class RoleUpdateIn(BaseModel):
    role: Role


class ActiveUpdateIn(BaseModel):
    active: bool
