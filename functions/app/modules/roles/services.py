import unicodedata

from app.core.firebase import get_db, snapshot_data

from .schemas import PermissionGroupOut, UserRoleCreateIn, UserRoleOut

ROLES_COLLECTION = "user_roles"
GROUPS_COLLECTION = "permission_groups"

# Bootstrap RBAC data: without at least the "admin" role, nobody could ever be
# granted a permission, so `system.factory_reset()` restores this right after
# wiping the database (see seed_defaults()). scripts/seed_rbac.py also uses
# this data for the initial, one-off setup of a brand new project.
PERMISSION_GROUPS = {
    "CASHBOX_BASIC": {
        "name": "Caja - Operación básica",
        "description": "Ver saldo, crear gastos/ingresos, editar/eliminar borradores propios",
    },
    "CASHBOX_MANAGE": {
        "name": "Caja - Gestión",
        "description": "Revisar pendientes, confirmar y eliminar cualquier movimiento",
    },
    "SYSTEM_ADMIN": {
        "name": "Administración del sistema",
        "description": "Gestionar usuarios, roles y grupos de permisos",
    },
}

USER_ROLES = {
    "admin": {
        "name": "Administrador",
        "description": "Acceso total a la aplicación",
        "group_ids": ["CASHBOX_BASIC", "CASHBOX_MANAGE", "SYSTEM_ADMIN"],
    },
    "manager": {
        "name": "Manager",
        "description": "Gestión de la caja y revisión de movimientos",
        "group_ids": ["CASHBOX_BASIC", "CASHBOX_MANAGE"],
    },
    "employee": {
        "name": "Empleado",
        "description": "Operación básica de la caja",
        "group_ids": ["CASHBOX_BASIC"],
    },
}


def seed_defaults() -> None:
    """(Re)writes the built-in permission groups and roles. Idempotent — safe
    to call on an existing project (e.g. after a factory reset) as well as a
    brand new one."""
    db = get_db()
    for code, fields in PERMISSION_GROUPS.items():
        db.collection(GROUPS_COLLECTION).document(code).set({"code": code, **fields})
    for slug, fields in USER_ROLES.items():
        db.collection(ROLES_COLLECTION).document(slug).set(fields)


def list_roles() -> list[UserRoleOut]:
    docs = get_db().collection(ROLES_COLLECTION).stream()
    return [UserRoleOut(id=doc.id, **snapshot_data(doc)) for doc in docs]


def list_permission_groups() -> list[PermissionGroupOut]:
    docs = get_db().collection(GROUPS_COLLECTION).stream()
    return [PermissionGroupOut(**snapshot_data(doc)) for doc in docs]


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
