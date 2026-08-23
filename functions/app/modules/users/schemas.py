from typing import Literal

from pydantic import BaseModel

UserStatus = Literal["active", "inactive", "new", "all"]


class UserOut(BaseModel):
    uid: str
    email: str | None
    display_name: str | None
    photo_url: str | None
    role_id: str | None
    disabled: bool


class UserListOut(BaseModel):
    users: list[UserOut]
    next_page_token: str | None = None


class RoleUpdateIn(BaseModel):
    role_id: str | None


class ActiveUpdateIn(BaseModel):
    active: bool
