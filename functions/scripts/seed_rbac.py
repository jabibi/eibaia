"""One-off script: seeds the permission_groups / user_roles Firestore collections
and migrates existing Firebase Auth users' `role` custom claim to `role_id`.
NOT a Cloud Function — run manually, once, against a target project.

Usage (from functions/):
    venv/bin/python scripts/seed_rbac.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # functions/ on sys.path

from firebase_admin import auth as firebase_auth  # noqa: E402

from app.core.firebase import get_db  # noqa: E402  (also initializes the Admin SDK)

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
        "description": "Gestión de la caja fuerte y revisión de movimientos",
        "group_ids": ["CASHBOX_BASIC", "CASHBOX_MANAGE"],
    },
    "empleado": {
        "name": "Empleado",
        "description": "Operación básica de la caja fuerte",
        "group_ids": ["CASHBOX_BASIC"],
    },
}

ROLE_CLAIM_MAP = {"admin": "admin", "manager": "manager", "user": "empleado"}


def seed_permission_groups(db) -> None:
    for code, fields in PERMISSION_GROUPS.items():
        db.collection("permission_groups").document(code).set({"code": code, **fields})
        print(f"  permission_groups/{code} seeded")


def seed_user_roles(db) -> None:
    for slug, fields in USER_ROLES.items():
        db.collection("user_roles").document(slug).set(fields)
        print(f"  user_roles/{slug} seeded")


def migrate_user_claims() -> None:
    for user in firebase_auth.list_users().iterate_all():
        claims = dict(user.custom_claims or {})
        if "role" not in claims:
            continue  # already migrated, or never had a role assigned
        old_role = claims.pop("role")
        claims["role_id"] = ROLE_CLAIM_MAP.get(old_role)
        firebase_auth.set_custom_user_claims(user.uid, claims)
        print(f"  {user.email or user.uid}: role={old_role!r} -> role_id={claims['role_id']!r}")


def main() -> None:
    db = get_db()
    print("Seeding permission_groups...")
    seed_permission_groups(db)
    print("Seeding user_roles...")
    seed_user_roles(db)
    print("Migrating Firebase Auth user claims (role -> role_id)...")
    migrate_user_claims()
    print("Done.")


if __name__ == "__main__":
    main()
