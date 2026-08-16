from pydantic import BaseModel


class PermissionGroupOut(BaseModel):
    code: str
    name: str
    description: str


class UserRoleOut(BaseModel):
    id: str
    name: str
    description: str
    group_ids: list[str]


class UserRoleCreateIn(BaseModel):
    name: str
    description: str
    group_ids: list[str]
