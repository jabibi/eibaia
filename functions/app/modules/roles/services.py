import unicodedata

from app.core.firebase import get_db

from .schemas import PermissionGroupOut, UserRoleCreateIn, UserRoleOut

ROLES_COLLECTION = "user_roles"
GROUPS_COLLECTION = "permission_groups"


def list_roles() -> list[UserRoleOut]:
    docs = get_db().collection(ROLES_COLLECTION).stream()
    return [UserRoleOut(id=doc.id, **doc.to_dict()) for doc in docs]


def list_permission_groups() -> list[PermissionGroupOut]:
    docs = get_db().collection(GROUPS_COLLECTION).stream()
    return [PermissionGroupOut(**doc.to_dict()) for doc in docs]


def _slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "_".join(normalized.lower().split())


def create_role(payload: UserRoleCreateIn) -> UserRoleOut:
    db = get_db()
    known_codes = {doc.id for doc in db.collection(GROUPS_COLLECTION).stream()}
    unknown = set(payload.group_ids) - known_codes
    if unknown:
        raise ValueError(f"Unknown permission group codes: {sorted(unknown)}")

    slug = _slugify(payload.name)
    doc_ref = db.collection(ROLES_COLLECTION).document(slug)
    if doc_ref.get().exists:
        raise ValueError(f"A role with id '{slug}' already exists")

    doc_ref.set({"name": payload.name, "description": payload.description, "group_ids": payload.group_ids})
    return UserRoleOut(id=slug, name=payload.name, description=payload.description, group_ids=payload.group_ids)
